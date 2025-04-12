document.addEventListener("DOMContentLoaded", function () {
    const addToCartButtons = document.querySelectorAll('.add-to-cart');

    // Adding event listeners to all add-to-cart buttons
    addToCartButtons.forEach(button => {
        button.addEventListener('click', function () {
            const productId = button.getAttribute('data-product-id');
            addToCart(productId);
        });
    });

    // Function to add product to the cart via AJAX
    function addToCart(productId) {
        fetch("/add-to-cart/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCookie("csrftoken"),
            },
            body: JSON.stringify({ product_id: productId }),
        })
        .then(response => response.json())
        .then(data => {
            // If the response is successful
            if (data.success) {
                alert("Product added to cart!");
                // Optionally, update the cart UI, such as cart counter or cart items display
            } else {
                // If there was an error on the server side
                alert("There was an error adding the product to the cart.");
                console.error("Error details:", data.error || "Unknown error");
            }
        })
        .catch(error => {
            // Catch any network or unexpected errors
            console.error("Error:", error);
            alert("An error occurred while processing your request.");
        });
    }

    // Function to get the CSRF token from cookies
    function getCookie(name) {
        const cookieValue = document.cookie
            .split('; ')
            .find(row => row.startsWith(name + "="))
            ?.split('=')[1];
        return cookieValue;
    }
});
