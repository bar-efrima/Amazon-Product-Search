const searchForm = document.querySelector('#search-form');
const tableContainer = document.getElementById('table-container');
const pricesTableContainer = document.getElementById('prices-table-container');

const homeLink = document.getElementById('home-link');

homeLink.addEventListener('click', event => {
    event.preventDefault();
    showPage(true, false);
});

searchForm.addEventListener('submit', event => {
    event.preventDefault();
    tableContainer.innerHTML = '';
    pricesTableContainer.innerHTML = ''; // Add this line to clear the pricesTableContainer
    const query = searchForm.elements.query.value;
    const encodedQuery = encodeURIComponent(query.replace(/ /g, '+'));
    fetch(`http://127.0.0.1:8000/search?query=${encodedQuery}`)
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                // Show error message
                const errorDiv = document.createElement('div');
                errorDiv.className = 'error-message';
                errorDiv.textContent = data.error;
                tableContainer.appendChild(errorDiv);
            } else {
                const table = document.createElement('table');
                tableContainer.appendChild(table);
                const headerRow = document.createElement('tr');
                const radioHeader = document.createElement('th');
                const nameHeader = document.createElement('th');
                nameHeader.textContent = 'Product Name';
                const imageHeader = document.createElement('th');
                imageHeader.textContent = 'Image URL';
                headerRow.appendChild(radioHeader);
                headerRow.appendChild(nameHeader);
                headerRow.appendChild(imageHeader);
                table.appendChild(headerRow);
                data.forEach(product => {
                    const row = document.createElement('tr');
                    const radioCell = document.createElement('td');
                    const radioButton = document.createElement('input');
                    radioButton.type = 'radio';
                    radioButton.name = 'product';
                    radioButton.value = product.asin;
                    radioCell.appendChild(radioButton);
                    row.appendChild(radioCell);
                    const nameCell = document.createElement('td');
                    nameCell.textContent = product.name;
                    const imageCell = document.createElement('td');
                    const image = document.createElement('img');
                    image.src = product.image_url;
                    image.alt = product.name;
                    image.width = 100;
                    imageCell.appendChild(image);
                    row.appendChild(nameCell);
                    row.appendChild(imageCell);
                    table.appendChild(row);
            });
         }
    });
});

function showPage(homeVisible, pastSearchesVisible) {
    const homePage = document.getElementById('home-page');
    const pastSearchesPage = document.getElementById('past-searches-page');
    homePage.style.display = homeVisible ? 'block' : 'none';
    pastSearchesPage.style.display = pastSearchesVisible ? 'block' : 'none';
}

tableContainer.addEventListener('click', event => {
    if (event.target.tagName === 'INPUT' && event.target.type === 'radio') {
        pricesTableContainer.innerHTML = ''; // Add this line to clear the pricesTableContainer
        const asin = event.target.value;
        const item_name = event.target.closest('tr').children[1].textContent; // Get the item_name from the selected row
        const query = searchForm.elements.query.value;
        fetch(`http://127.0.0.1:8000/get_prices?asin=${asin}&query=${encodeURIComponent(query)}&item_name=${encodeURIComponent(item_name)}`)
            .then(response => response.json())
            .then(data => {
                const pricesTable = document.createElement('table');
                pricesTableContainer.appendChild(pricesTable);
                const headerRow = document.createElement('tr');
                const headers = ['Item', 'Rating', 'Amazon.com', 'Amazon.co.uk', 'Amazon.de', 'Amazon.ca'];
                headers.forEach(header => {
                    const th = document.createElement('th');
                    th.textContent = header;
                    headerRow.appendChild(th);
                });
                pricesTable.appendChild(headerRow);
                const dataRow = document.createElement('tr');

                 for (let key of headers) {
                    const td = document.createElement('td');
                    if (key in data['Prices']) {
                        if (data['Prices'][key] !== 'Not found') { // Check if the price is available
                            // Create a hyperlink for the price
                            const priceLink = document.createElement('a');
                            priceLink.href = data['URLs'][key];
                            priceLink.target = '_blank';
                            priceLink.textContent = data['Prices'][key];
                            td.appendChild(priceLink);
                        } else {
                            td.textContent = data['Prices'][key]; // Add 'Not found' text without hyperlink
                        }
                    } else {
                        td.textContent = data[key];
                    }
                    dataRow.appendChild(td);
                }
                pricesTable.appendChild(dataRow);
            });
    }
});


const pastSearchesLink = document.getElementById('past-searches-link');
const pastSearchesContainer = document.getElementById('past-searches-container');

pastSearchesLink.addEventListener('click', event => {
    event.preventDefault();
    pastSearchesContainer.innerHTML = '';
    console.log("Fetching past searches");
    showPage(false, true);
    fetch('http://127.0.0.1:8000/past_searches')
        .then(response => {
            console.log("Response received", response);
            return response.json();
        })
        .then(data => {
            console.log("Data received", data);
            const table = document.createElement('table');
            pastSearchesContainer.appendChild(table);
            const headerRow = document.createElement('tr');
            const headers = ['Query', 'Time', 'Item name', 'Amazon.com price', 'Amazon.co.uk price', 'Amazon.de price', 'Amazon.ca price'];
            headers.forEach(header => {
                const th = document.createElement('th');
                th.textContent = header;
                headerRow.appendChild(th);
            });
            table.appendChild(headerRow);

            data.forEach(search => {
                const row = document.createElement('tr');
                headers.forEach(header => {
                    const td = document.createElement('td');
                     if (['Amazon.com price', 'Amazon.co.uk price', 'Amazon.de price', 'Amazon.ca price'].includes(header)) {
                        // Add a $ sign to the price if it exists
                        td.textContent = search[header] ? `$${search[header]}` : search[header];
                    } else {
                        td.textContent = header === 'Query' ? search[header].replace(/\+/g, ' ') : search[header];
                    }
                    row.appendChild(td);
                });
                table.appendChild(row);
            });
        });
});
