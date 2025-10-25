// Currency configuration
const CURRENCY_SYMBOLS = {
    'GBP': '£',
    'USD': '$',
    'EUR': '€'
};

let items = [];
let currentChart = null;
// View state management
let currentView = localStorage.getItem('wishlist-view') || 'grid';

function setView(view) {
    currentView = view;
    localStorage.setItem('wishlist-view', view);
    
    // Update button states
    document.getElementById('grid-view-btn').classList.toggle('active', view === 'grid');
    document.getElementById('list-view-btn').classList.toggle('active', view === 'list');
    
    // Re-render items with new view
    renderItems();
}

function initializeView() {
    // Set initial button states
    document.getElementById('grid-view-btn').classList.toggle('active', currentView === 'grid');
    document.getElementById('list-view-btn').classList.toggle('active', currentView === 'list');
}

// Load items on page load
document.addEventListener('DOMContentLoaded', () => {
    initializeView();
    loadItems();
});

async function loadItems() {
    try {
        const response = await fetch('/api/items');
        items = await response.json();
        renderItems();
    } catch (error) {
        console.error('Error loading items:', error);
    }
}

function getCurrencySymbol(currency) {
    return CURRENCY_SYMBOLS[currency] || currency;
}

function calculateTotals() {
    const totalItems = items.length;
    const itemsWithPrices = items.filter(item => item.current_price).length;
    
    // Calculate totals per currency
    const currencyTotals = {};
    items.forEach(item => {
        if (item.current_price && item.currency) {
            if (!currencyTotals[item.currency]) {
                currencyTotals[item.currency] = 0;
            }
            currencyTotals[item.currency] += item.current_price;
        }
    });
    
    return {
        totalItems,
        itemsWithPrices,
        currencyTotals
    };
}

function updateSummary() {
    const summary = calculateTotals();
    const summaryPanel = document.getElementById('summary-panel');
    
    // Show/hide panel based on whether there are items
    if (summary.totalItems === 0) {
        summaryPanel.style.display = 'none';
        return;
    }
    
    summaryPanel.style.display = 'block';
    
    // Update stats
    document.getElementById('total-items').textContent = summary.totalItems;
    document.getElementById('items-with-prices').textContent = summary.itemsWithPrices;
    
    // Update currency breakdown
    const breakdownContainer = document.getElementById('currency-breakdown');
    
    if (Object.keys(summary.currencyTotals).length === 0) {
        breakdownContainer.innerHTML = '<div style="opacity: 0.8; font-size: 0.95em;">No items with prices yet</div>';
    } else {
        breakdownContainer.innerHTML = Object.entries(summary.currencyTotals)
            .map(([currency, total]) => {
                const symbol = getCurrencySymbol(currency);
                return `
                    <div class="currency-item">
                        <div class="currency-symbol">${symbol}</div>
                        <div class="currency-amount">${total.toFixed(2)}</div>
                        <div style="opacity: 0.8; font-size: 0.9em;">${currency}</div>
                    </div>
                `;
            })
            .join('');
    }
}

function renderItems() {
    const container = document.getElementById('items-container');
    
    if (items.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4"></path>
                </svg>
                <h3>Your wishlist is empty</h3>
                <p>Add your first item to start tracking prices!</p>
            </div>
        `;
        updateSummary();
        return;
    }

    // Set container class based on view
    container.className = currentView === 'list' ? 'items-list' : 'items-grid';
    
    if (currentView === 'list') {
        container.innerHTML = items.map(item => renderListItem(item)).join('');
    } else {
        container.innerHTML = items.map(item => renderGridItem(item)).join('');
    }
    
    updateSummary();
}

function renderGridItem(item) {
    const currencySymbol = getCurrencySymbol(item.currency);
    return `
        <div class="item-card">
            ${item.image_path ? `<img src="/${item.image_path}" class="item-image" alt="${item.item_name}">` : '<div class="item-image"></div>'}
            <div class="item-type">${item.item_type}</div>
            <div class="item-name">${item.item_name}</div>
            ${item.current_price ? `<div class="item-price">${currencySymbol}${item.current_price.toFixed(2)}</div>` : ''}
            ${item.last_checked ? `<div class="last-checked">Last checked: ${new Date(item.last_checked).toLocaleDateString()}</div>` : ''}
            ${item.url ? `<a href="${item.url}" target="_blank" style="color: #667eea; text-decoration: none;">View Product →</a>` : ''}
            <div class="item-actions">
                ${item.url ? `<button onclick="checkPrice(${item.id})">Check Price</button>` : ''}
                <button onclick="showHistory(${item.id})">History</button>
                <button onclick="deleteItem(${item.id})" style="background: #f56565;">Delete</button>
            </div>
        </div>
    `;
}

function renderListItem(item) {
    const currencySymbol = getCurrencySymbol(item.currency);
    const createdDate = new Date(item.created_at).toLocaleDateString();
    const lastCheckedDate = item.last_checked ? new Date(item.last_checked).toLocaleDateString() : 'Never';
    
    return `
        <div class="item-card">
            ${item.image_path ? `<img src="/${item.image_path}" class="item-image" alt="${item.item_name}">` : '<div class="item-image"></div>'}
            
            <div class="item-details">
                <div>
                    <span class="item-type">${item.item_type}</span>
                </div>
                <div class="item-name">${item.item_name}</div>
                ${item.current_price ? `<div class="item-price">${currencySymbol}${item.current_price.toFixed(2)} ${item.currency}</div>` : '<div style="color: #999;">No price set</div>'}
                
                <div class="item-meta">
                    <div class="item-meta-item">
                        <span class="item-meta-label">Added:</span>
                        <span>${createdDate}</span>
                    </div>
                    <div class="item-meta-item">
                        <span class="item-meta-label">Last Checked:</span>
                        <span>${lastCheckedDate}</span>
                    </div>
                </div>
                
                ${item.url ? `<a href="${item.url}" target="_blank" style="color: #667eea; text-decoration: none;">🔗 View Product</a>` : ''}
            </div>
            
            <div class="item-actions">
                ${item.url ? `<button onclick="checkPrice(${item.id})">Check Price</button>` : ''}
                <button onclick="showHistory(${item.id})">History</button>
                <button onclick="deleteItem(${item.id})" style="background: #f56565;">Delete</button>
            </div>
        </div>
    `;
}

function openAddModal() {
    document.getElementById('add-modal').classList.add('active');
}

function closeAddModal() {
    document.getElementById('add-modal').classList.remove('active');
    document.getElementById('add-form').reset();
}

async function addItem(event) {
    event.preventDefault();
    
    const formData = new FormData();
    formData.append('item_type', document.getElementById('item-type').value);
    formData.append('item_name', document.getElementById('item-name').value);
    formData.append('url', document.getElementById('item-url').value);
    formData.append('current_price', document.getElementById('current-price').value);
    formData.append('currency', document.getElementById('item-currency').value);
    formData.append('auto_fetch_image', document.getElementById('auto-fetch-image').checked);
    
    const imageFile = document.getElementById('item-image').files[0];
    if (imageFile) {
        formData.append('image', imageFile);
    }
    
    try {
        const response = await fetch('/api/items', {
            method: 'POST',
            body: formData
        });
        
        if (response.ok) {
            closeAddModal();
            loadItems();
        }
    } catch (error) {
        console.error('Error adding item:', error);
        alert('Failed to add item. Please try again.');
    }
}

async function deleteItem(id) {
    if (!confirm('Are you sure you want to delete this item?')) {
        return;
    }
    
    try {
        const response = await fetch(`/api/items/${id}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            loadItems();
        }
    } catch (error) {
        console.error('Error deleting item:', error);
        alert('Failed to delete item. Please try again.');
    }
}

async function checkPrice(id) {
    const button = event.target;
    button.disabled = true;
    button.textContent = 'Checking...';
    
    try {
        const response = await fetch(`/api/items/${id}/check-price`, {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (data.success) {
            const item = items.find(i => i.id === id);
            const currencySymbol = getCurrencySymbol(item.currency);
            alert(`Price updated: ${currencySymbol}${data.price.toFixed(2)}`);
            loadItems();
        } else {
            alert('Could not fetch price from URL. Please check manually.');
        }
    } catch (error) {
        console.error('Error checking price:', error);
        alert('Failed to check price. Please try again.');
    } finally {
        button.disabled = false;
        button.textContent = 'Check Price';
    }
}

async function checkAllPrices() {
    const button = event.target;
    button.disabled = true;
    button.textContent = 'Checking...';
    
    try {
        const itemsWithUrls = items.filter(item => item.url);
        let successCount = 0;
        
        for (const item of itemsWithUrls) {
            const response = await fetch(`/api/items/${item.id}/check-price`, {
                method: 'POST'
            });
            
            if (response.ok) {
                successCount++;
            }
        }
        
        alert(`Updated ${successCount} of ${itemsWithUrls.length} items.`);
        loadItems();
    } catch (error) {
        console.error('Error checking prices:', error);
        alert('Failed to check prices. Please try again.');
    } finally {
        button.disabled = false;
        button.textContent = '🔄 Check All Prices';
    }
}

async function showHistory(id) {
    try {
        const response = await fetch(`/api/items/${id}/price-history`);
        const history = await response.json();
        
        if (history.length === 0) {
            alert('No price history available for this item.');
            return;
        }
        
        const item = items.find(i => i.id === id);
        const currencySymbol = getCurrencySymbol(item.currency);
        
        const labels = history.map(h => new Date(h.checked_at).toLocaleDateString());
        const prices = history.map(h => h.price);
        
        if (currentChart) {
            currentChart.destroy();
        }
        
        const ctx = document.getElementById('price-chart').getContext('2d');
        currentChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: `Price (${currencySymbol})`,
                    data: prices,
                    borderColor: '#667eea',
                    backgroundColor: 'rgba(102, 126, 234, 0.1)',
                    tension: 0.4,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: true,
                        position: 'top'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: false,
                        ticks: {
                            callback: function(value) {
                                return currencySymbol + value.toFixed(2);
                            }
                        }
                    }
                }
            }
        });
        
        document.getElementById('history-modal').classList.add('active');
    } catch (error) {
        console.error('Error fetching history:', error);
        alert('Failed to load price history. Please try again.');
    }
}

function closeHistoryModal() {
    document.getElementById('history-modal').classList.remove('active');
}

async function exportCSV() {
    try {
        window.location.href = '/api/export/csv';
    } catch (error) {
        console.error('Error exporting CSV:', error);
        alert('Failed to export CSV. Please try again.');
    }
}

// Close modals on background click
document.querySelectorAll('.modal').forEach(modal => {
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.classList.remove('active');
        }
    });
});