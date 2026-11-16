// Interatividade e melhorias de UX para a plataforma Recomeço Animal

document.addEventListener('DOMContentLoaded', function () {
    // 1. Troca de foto principal na galeria da página de detalhes do animal
    const mainImg = document.getElementById('mainAnimalImage');
    const thumbnails = document.querySelectorAll('.gallery-thumbnail');

    if (mainImg && thumbnails.length > 0) {
        thumbnails.forEach(thumb => {
            thumb.addEventListener('click', function () {
                // Atualiza a imagem principal com a URL do thumbnail
                const newSrc = this.getAttribute('data-full-img') || this.src;
                mainImg.src = newSrc;

                // Atualiza classe ativa
                thumbnails.forEach(t => t.classList.remove('active'));
                this.classList.add('active');
            });
        });
    }

    // 2. Auto-dismiss em alertas informativos após 6 segundos
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(alert => {
        setTimeout(() => {
            try {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            } catch (e) {
                // fallback caso bootstrap já tenha tratado
            }
        }, 7000);
    });

    // 3. Suavização de scroll em links com âncoras internas
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            const targetId = this.getAttribute('href');
            if (targetId && targetId !== '#') {
                const targetElement = document.querySelector(targetId);
                if (targetElement) {
                    e.preventDefault();
                    targetElement.scrollIntoView({
                        behavior: 'smooth'
                    });
                }
            }
        });
    });
});

