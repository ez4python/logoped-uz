// Handle file input for profile image
document.addEventListener("DOMContentLoaded", () => {
    // Profile image upload preview
    const imageInput = document.getElementById("id_image")
    if (imageInput) {
        imageInput.addEventListener("change", function () {
            if (this.files && this.files[0]) {
                const reader = new FileReader()
                reader.onload = (e) => {
                    const profileImage = document.querySelector(".avatar img")
                    if (profileImage) {
                        profileImage.src = e.target.result
                    } else {
                        const avatarContainer = document.querySelector(".avatar")
                        if (avatarContainer) {
                            avatarContainer.innerHTML = `<img src="${e.target.result}" alt="Profile" class="w-full h-full object-cover">`
                        }
                    }
                }
                reader.readAsDataURL(this.files[0])
            }
        })
    }

    // Auto-focus on first verification code input
    const firstCodeInput = document.getElementById("code_0")
    if (firstCodeInput) {
        setTimeout(() => {
            firstCodeInput.focus()
        }, 300)
    }

    // Handle verification code inputs
    const codeInputs = document.querySelectorAll(".verification-code-input")
    if (codeInputs.length) {
        codeInputs.forEach((input, index) => {
            // Focus next input when current one is filled
            input.addEventListener("input", function () {
                if (this.value.length === this.maxLength) {
                    const nextInput = codeInputs[index + 1]
                    if (nextInput) {
                        nextInput.focus()
                    }
                }
            })

            // Handle backspace to go to previous input
            input.addEventListener("keydown", function (e) {
                if (e.key === "Backspace" && !this.value) {
                    const prevInput = codeInputs[index - 1]
                    if (prevInput) {
                        prevInput.focus()
                    }
                }
            })
        })
    }
})
