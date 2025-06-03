document.addEventListener("DOMContentLoaded", () => {
    // Получаем все поля ввода кода
    const codeInputs = document.querySelectorAll('input[id^="code_"]')

    // Добавляем обработчики событий для каждого поля
    codeInputs.forEach((input, index) => {
        // При вводе символа переходим к следующему полю
        input.addEventListener("input", function (e) {
            if (this.value.length === this.maxLength && index < codeInputs.length - 1) {
                codeInputs[index + 1].focus()
            }
        })

        // При нажатии Backspace в пустом поле переходим к предыдущему полю
        input.addEventListener("keydown", function (e) {
            if (e.key === "Backspace" && this.value.length === 0 && index > 0) {
                codeInputs[index - 1].focus()
            }
        })

        // Обработка вставки кода
        input.addEventListener("paste", (e) => {
            e.preventDefault()
            const pastedData = e.clipboardData.getData("text/plain").replace(/\D/g, "").slice(0, 6)

            if (pastedData) {
                // Распределяем вставленные цифры по полям
                for (let i = 0; i < pastedData.length && i < codeInputs.length; i++) {
                    codeInputs[i].value = pastedData[i]
                }

                // Устанавливаем фокус на последнее заполненное поле или следующее пустое
                const focusIndex = Math.min(pastedData.length, codeInputs.length - 1)
                codeInputs[focusIndex].focus()
            }
        })
    })
})
