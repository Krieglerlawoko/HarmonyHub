document.addEventListener('DOMContentLoaded', function() {
    // Function to fetch recommendations based on genre
    function getRecommendations(genre) {
        fetch('/recommend', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ genre: genre })
        })
        .then(response => response.json())
        .then(data => {
            // Clear previous recommendations
            const recommendationsDiv = document.getElementById('recommendations');
            recommendationsDiv.innerHTML = '';

            // Display new recommendations
            data.forEach(song => {
                const p = document.createElement('p');
                p.textContent = `${song.title} - ${song.artist}`;
                recommendationsDiv.appendChild(p);
            });
        })
        .catch(error => console.error('Error:', error));
    }

    // Event listener for the genre selection dropdown
    const genreSelect = document.getElementById('genre');
    genreSelect.addEventListener('change', function() {
        const selectedGenre = genreSelect.value;
        getRecommendations(selectedGenre);
    });

    // Initial recommendations load
    getRecommendations(genreSelect.value);
});
