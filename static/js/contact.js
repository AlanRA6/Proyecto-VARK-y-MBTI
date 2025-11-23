    // SCRIPT PARA MANEJAR EL ENVÍO SIN RECARGAR LA PÁGINA
    const form = document.getElementById("contact-form");
    
    async function handleSubmit(event) {
        event.preventDefault();
        const status = document.getElementById("form-status");
        const btn = document.getElementById("submit-btn");
        const data = new FormData(event.target);

        // Cambiar botón a estado de carga
        btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Enviando...';
        btn.disabled = true;

        fetch(event.target.action, {
            method: form.method,
            body: data,
            headers: {
                'Accept': 'application/json'
            }
        }).then(response => {
            if (response.ok) {
                status.innerHTML = "¡Gracias! Tu mensaje ha sido enviado.";
                status.style.color = "green";
                form.reset(); // Limpiar formulario
            } else {
                response.json().then(data => {
                    if (Object.hasOwn(data, 'errors')) {
                        status.innerHTML = data["errors"].map(error => error["message"]).join(", ")
                    } else {
                        status.innerHTML = "Hubo un problema al enviar el formulario."
                    }
                    status.style.color = "#a80000";
                })
            }
        }).catch(error => {
            status.innerHTML = "Error de conexión. Intenta de nuevo.";
            status.style.color = "#a80000";
        }).finally(() => {
            // Restaurar botón
            btn.innerHTML = 'Enviar Mensaje';
            btn.disabled = false;
        });
    }

    form.addEventListener("submit", handleSubmit);
