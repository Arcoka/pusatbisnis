

// Script untuk membuat pengalaman hover yang juga bekerja di perangkat sentuh
        document.addEventListener('DOMContentLoaded', function() {
            const heroContainer = document.querySelector('.hero-container');
            const imageContainer = document.querySelector('.hero-image-container');

            // Toggle class untuk perangkat sentuh
            imageContainer.addEventListener('touchstart', function() {
                heroContainer.classList.toggle('touch-active');
                if (heroContainer.classList.contains('touch-active')) {
                    heroContainer.querySelector('.hero-content').style.width = '50%';
                    heroContainer.querySelector('.hero-image-container').style.width = '50%';
                } else {
                    heroContainer.querySelector('.hero-content').style.width = '70%';
                    heroContainer.querySelector('.hero-image-container').style.width = '30%';
                }
            });
        });

 // LAYANAN
  document.addEventListener('DOMContentLoaded', function() {
            const sliderTrack = document.querySelector('.slider-track');

            // Force hardware acceleration
            sliderTrack.style.transform = 'translateZ(0)';

            // Handle reduced motion
            if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
                sliderTrack.style.animationDuration = '50s';
            }

            console.log('Slider initialized successfully');
        });

const track = document.querySelector('.slider-track');
const cards = track.querySelectorAll('.card');

// Ambil nilai dari CSS variable yang sudah kamu set
const cardWidth = parseInt(getComputedStyle(document.documentElement).getPropertyValue('--card-width'));
const gap = parseInt(getComputedStyle(document.documentElement).getPropertyValue('--gap'));

const cardCount = cards.length;
const halfCount = cardCount / 2;

// Hitung total lebar semua kartu + semua gap
const totalWidth = (cardWidth * cardCount) + (gap * (cardCount - 1));

// Hitung slide distance untuk 6 kartu pertama + 5 gap
const slideDistance = (cardWidth * halfCount) + (gap * (halfCount - 1));

// Masukkan ke dalam variabel CSS di elemen .slider-track
track.style.setProperty('--track-width', `${totalWidth}px`);
track.style.setProperty('--slide-distance', `${slideDistance}px`);

// ================== Extracted from beranda.html ==================
// Team auto-scroll pause/resume handlers
(function() {
  const teamContainer = document.querySelector('.team-scroll-container');
  const teamWrapper = document.querySelector('.team-scroll-wrapper');

  if (teamContainer && teamWrapper) {
    let touchStartX = 0;
    let touchEndX = 0;

    teamContainer.addEventListener('touchstart', (e) => {
      touchStartX = e.changedTouches[0].screenX;
      teamWrapper.style.animationPlayState = 'paused';
    }, { passive: true });

    teamContainer.addEventListener('touchend', (e) => {
      touchEndX = e.changedTouches[0].screenX;
      setTimeout(() => {
        teamWrapper.style.animationPlayState = 'running';
      }, 1000);
    });

    teamContainer.addEventListener('mouseenter', () => {
      teamWrapper.style.animationPlayState = 'paused';
    });

    teamContainer.addEventListener('mouseleave', () => {
      teamWrapper.style.animationPlayState = 'running';
    });
  }
})();

// Testimonials carousel logic
(function() {
  document.addEventListener('DOMContentLoaded', function () {
    const track = document.querySelector('.testimonial-track');
    const cards = document.querySelectorAll('.testimonial-card');
    const dots = document.querySelectorAll('.dot');
    const prevButton = document.querySelector('.prev-button');
    const nextButton = document.querySelector('.next-button');

    if (!track || !cards.length) return;

    let currentIndex = 0;
    const cardCount = cards.length;

    function updateCarousel() {
      track.style.transform = `translateX(${-currentIndex * 100}%)`;
      dots.forEach((dot, index) => {
        dot.classList.toggle('active', index === currentIndex);
      });
    }

    updateCarousel();

    if (prevButton) {
      prevButton.addEventListener('click', function () {
        currentIndex = (currentIndex - 1 + cardCount) % cardCount;
        updateCarousel();
      });
    }

    if (nextButton) {
      nextButton.addEventListener('click', function () {
        currentIndex = (currentIndex + 1) % cardCount;
        updateCarousel();
      });
    }

    dots.forEach((dot, index) => {
      dot.addEventListener('click', function () {
        currentIndex = index;
        updateCarousel();
      });
    });

    let interval = setInterval(() => {
      currentIndex = (currentIndex + 1) % cardCount;
      updateCarousel();
    }, 5000);

    const carousel = document.querySelector('.testimonial-carousel');
    if (carousel) {
      carousel.addEventListener('mouseenter', () => { clearInterval(interval); });
      carousel.addEventListener('mouseleave', () => {
        interval = setInterval(() => {
          currentIndex = (currentIndex + 1) % cardCount;
          updateCarousel();
        }, 5000);
      });

      let touchStartX = 0;
      let touchEndX = 0;
      carousel.addEventListener('touchstart', e => { touchStartX = e.changedTouches[0].screenX; }, { passive: true });
      carousel.addEventListener('touchend', e => {
        touchEndX = e.changedTouches[0].screenX;
        const swipeThreshold = 50;
        if (touchEndX < touchStartX - swipeThreshold) {
          currentIndex = (currentIndex + 1) % cardCount;
          updateCarousel();
        } else if (touchEndX > touchStartX + swipeThreshold) {
          currentIndex = (currentIndex - 1 + cardCount) % cardCount;
          updateCarousel();
        }
      });
    }
  });
})();

// BAGIAN BERITA DETAIL

// Store original descriptions for each image type
    const descriptions = {
        'main': `{{ berita.deskripsi|safe|escapejs }}`,
        'gambar_1': `{{ berita.deskripsi_1|safe|escapejs|default:berita.deskripsi|safe|escapejs }}`,
        'gambar_2': `{{ berita.deskripsi_2|safe|escapejs|default:berita.deskripsi|safe|escapejs }}`,
        'gambar_3': `{{ berita.deskripsi_3|safe|escapejs|default:berita.deskripsi|safe|escapejs }}`
    };

    // Function to adjust image heights based on thumbnail count
    function adjustImageHeights() {
        const totalImages = document.querySelectorAll('.thumbnail-card').length;
        const mainImageSection = document.getElementById('mainImageSection');
        const thumbnailsSection = document.getElementById('thumbnailsSection');
        
        if (!mainImageSection || !thumbnailsSection) return;
        
        // Logic: Jika gambar > 3, tinggi ditambah. Jika ≤ 3, tinggi tetap
        if (totalImages > 3) {
            // Lebih dari 3 gambar - tinggi ditambah
            if (window.innerWidth >= 1024) {
                mainImageSection.style.height = '700px';
                thumbnailsSection.style.minHeight = '700px';
            } else if (window.innerWidth >= 768) {
                mainImageSection.style.height = '600px';
                thumbnailsSection.style.minHeight = '600px';
            } else {
                mainImageSection.style.height = '350px';
            }
        } else {
            // 3 gambar atau kurang - tinggi tetap (default)
            if (window.innerWidth >= 1024) {
                mainImageSection.style.height = '600px';
                thumbnailsSection.style.minHeight = '600px';
            } else if (window.innerWidth >= 768) {
                mainImageSection.style.height = '500px';
                thumbnailsSection.style.minHeight = '500px';
            } else {
                mainImageSection.style.height = '300px';
            }
        }
    }

    function changeMainImage(src, alt, imageType) {
        const mainImage = document.getElementById('mainImage');
        const fullDescription = document.getElementById('fullDescription');

        // Remove active class from all thumbnails
        document.querySelectorAll('.thumbnail-card').forEach(card => {
            card.classList.remove('active-thumbnail');
        });

        // Add active class to clicked thumbnail
        const clickedThumbnail = event.target.closest('.thumbnail-card');
        if (clickedThumbnail) {
            clickedThumbnail.classList.add('active-thumbnail');
        }

        // Add fade out effect
        if (mainImage) {
            mainImage.style.opacity = '0';
            mainImage.style.transform = 'scale(1.05)';

            setTimeout(() => {
                mainImage.src = src;
                mainImage.alt = alt;

                // Update full description
                if (descriptions[imageType]) {
                    const fullDescContent = fullDescription.querySelector('.content-text');
                    if (fullDescContent) {
                        fullDescContent.innerHTML = descriptions[imageType];
                    }
                }

                mainImage.style.opacity = '1';
                mainImage.style.transform = 'scale(1)';
            }, 300);
        }
    }

    function toggleFullDescription() {
        const fullDescription = document.getElementById('fullDescription');
        const button = document.querySelector('.read-more-btn');
        const btnText = button.querySelector('.btn-text');
        
        if (fullDescription.style.display === 'none' || !fullDescription.style.display) {
            fullDescription.style.display = 'block';
            btnText.textContent = 'Sembunyikan';
            button.classList.add('expanded');
            
            setTimeout(() => {
                const offsetTop = fullDescription.offsetTop - 20;
                window.scrollTo({
                    top: offsetTop,
                    behavior: 'smooth'
                });
            }, 100);
        } else {
            fullDescription.style.display = 'none';
            btnText.textContent = 'Lihat Selengkapnya';
            button.classList.remove('expanded');
            
            const articleTop = document.querySelector('.news-article').offsetTop - 100;
            window.scrollTo({
                top: articleTop,
                behavior: 'smooth'
            });
        }
    }

    // Initialize
    document.addEventListener('DOMContentLoaded', function () {
        // Set active thumbnail
        const firstThumbnail = document.querySelector('.thumbnail-card[data-type="main"]');
        if (firstThumbnail) {
            firstThumbnail.classList.add('active-thumbnail');
        }

        // Adjust heights after a short delay
        setTimeout(() => {
            adjustImageHeights();
        }, 500);

        // Add loading state management
        const mainImage = document.getElementById('mainImage');
        if (mainImage) {
            mainImage.addEventListener('load', function() {
                this.style.opacity = '1';
                this.style.transform = 'scale(1)';
            });
        }
    });

    // Handle resize events
    let resizeTimer;
    window.addEventListener('resize', function() {
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(() => {
            adjustImageHeights();
        }, 250);
    });

//BAGIAN FAQ

