document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.like-heart').forEach(function(heart) {
        heart.addEventListener('click', function(e) {
            if (heart.classList.contains('disabled')) return;
            const parent = heart.closest('.venue-likes-count');
            const venueId = parent.getAttribute('data-venue-id');
            fetch('/like-venue', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: JSON.stringify({ venue_id: venueId })
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    parent.querySelector('.likes-num').textContent = data.likes;
                    if (data.liked) {
                        heart.classList.add('liked');
                    } else {
                        heart.classList.remove('liked');
                    }
                }
            })
        });
    });
}); 