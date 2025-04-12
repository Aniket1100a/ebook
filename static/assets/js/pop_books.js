window.onload = function() {
    // Function to clone all books from other genre sections into the "All Genre" tab
    function cloneBooksToAllGenre() {
        // Get all genre sections
        var genreSections = document.querySelectorAll('[data-tab-content]');
        
        // Get the all-genre container
        var allGenreContainer = document.getElementById('all-genre-books');

        // Loop through each genre section
        genreSections.forEach(function(section) {
            if (section.id !== 'all-genre') {  // Avoid the "All Genre" section itself
                var books = section.querySelectorAll('.row > .col-md-3');
                
                // Loop through each book and append it to the all-genre section
                books.forEach(function(book) {
                    allGenreContainer.appendChild(book.cloneNode(true));
                });
            }
        });
    }

    // Clone books when the page loads
    cloneBooksToAllGenre();
};
