// Lightbox для venue-img-clickable

document.addEventListener('DOMContentLoaded', function() {
    const modal = document.getElementById('img-modal');
    const modalImg = document.getElementById('img-modal-full');
    const closeBtn = document.querySelector('.img-modal-close');
    document.querySelectorAll('.venue-img-clickable').forEach(img => {
        img.addEventListener('click', function() {
            modal.classList.add('open');
            modalImg.src = this.src;
            modalImg.alt = this.alt;
        });
    });
    if (closeBtn) closeBtn.addEventListener('click', function() {
        modal.classList.remove('open');
        modalImg.src = '';
    });
    if (modal) modal.addEventListener('click', function(e) {
        if (e.target === modal) {
            modal.classList.remove('open');
            modalImg.src = '';
        }
    });
}); 