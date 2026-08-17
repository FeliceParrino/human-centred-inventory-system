const productDataElement = document.getElementById('product-data');
const products = productDataElement ? JSON.parse(productDataElement.textContent) : [];

function setupAutocomplete(inputId, hiddenId, listId) {
    const input = document.getElementById(inputId);
    const hidden = document.getElementById(hiddenId);
    const list = document.getElementById(listId);

    if (!input || !hidden || !list) {
        return;
    }

    input.addEventListener('input', function() {
        const val = this.value.toLowerCase();
        hidden.value = '';
        list.innerHTML = '';

        if (!val) {
            list.style.display = 'none';
            return;
        }

        const matches = products.filter(product =>
            product.name.toLowerCase().includes(val)
        );

        if (!matches.length) {
            list.style.display = 'none';
            return;
        }

        matches.forEach(product => {
            const item = document.createElement('div');
            item.className = 'autocomplete-item';
            item.textContent = product.name;
            item.addEventListener('mousedown', () => {
                input.value = product.name;
                hidden.value = product.id;
                list.style.display = 'none';
            });
            list.appendChild(item);
        });

        list.style.display = 'block';
    });

    document.addEventListener('click', event => {
        if (!event.target.closest('#' + inputId) && !event.target.closest('#' + listId)) {
            list.style.display = 'none';
        }
    });
}

setupAutocomplete('restock-search', 'restock-id', 'restock-list');
setupAutocomplete('sell-search', 'sell-id', 'sell-list');
setupAutocomplete('price-search', 'price-id', 'price-list');

document.querySelectorAll('.delete-form').forEach(form => {
    form.addEventListener('submit', event => {
        const productName = form.dataset.productName || 'this product';
        const confirmed = confirm(
            `Are you sure you want to delete ${productName}? This action cannot be undone.`
        );

        if (!confirmed) {
            event.preventDefault();
        }
    });
});
