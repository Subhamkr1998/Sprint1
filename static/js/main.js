document.addEventListener('DOMContentLoaded', function() {
    // Fetch expenses data for charts and summary
    fetchExpenses();
    
    // Fetch monthly summary data
    fetchMonthlySummary();
    
    // Initialize search functionality
    initSearch();
});

// Fetch expenses data from the API
async function fetchExpenses() {
    try {
        const response = await fetch('/api/expenses');
        const expenses = await response.json();
        
        // Update summary metrics
        updateSummaryMetrics(expenses);
        
        // Fetch category data and update chart
        fetchCategoryData();
    } catch (error) {
        console.error('Error fetching expenses:', error);
    }
}

// Fetch monthly summary data from the API
async function fetchMonthlySummary() {
    try {
        const response = await fetch('/api/monthly_summary');
        const data = await response.json();
        
        // Update monthly summary metrics
        updateMonthlySummary(data);
    } catch (error) {
        console.error('Error fetching monthly summary:', error);
    }
}

// Update summary metrics based on expenses data
function updateSummaryMetrics(expenses) {
    const totalElement = document.getElementById('total-expenses');
    
    if (expenses.length === 0) {
        totalElement.textContent = '₹0.00';
        return;
    }
    
    // Calculate total with explicit number conversion
    const total = expenses.reduce((sum, expense) => sum + parseFloat(expense.amount), 0);
    
    // Update DOM elements
    totalElement.textContent = '₹' + total.toFixed(2);
}

// Update monthly summary metrics
function updateMonthlySummary(data) {
    const monthlyExpensesElement = document.getElementById('monthly-expenses');
    const monthlySavingsElement = document.getElementById('monthly-savings');
    const budgetPercentageElement = document.getElementById('budget-percentage');
    
    if (monthlyExpensesElement) {
        monthlyExpensesElement.textContent = '₹' + data.monthly_expenses.toFixed(2);
    }
    
    if (monthlySavingsElement) {
        monthlySavingsElement.textContent = '₹' + data.savings.toFixed(2);
    }
    
    if (budgetPercentageElement && data.monthly_budget > 0) {
        const percentage = (data.monthly_expenses / data.monthly_budget) * 100;
        budgetPercentageElement.textContent = percentage.toFixed(1) + '% of budget used';
        
        // Update budget progress bar
        const progressBar = budgetPercentageElement.parentElement.nextElementSibling.querySelector('div');
        if (progressBar) {
            if (percentage > 100) {
                progressBar.style.width = '100%';
                progressBar.className = 'bg-red-600 h-2.5 rounded-full';
            } else {
                progressBar.style.width = percentage + '%';
                progressBar.className = percentage > 90 ? 'bg-yellow-600 h-2.5 rounded-full' : 'bg-green-600 h-2.5 rounded-full';
            }
        }
    }
}

// Fetch category data for the pie chart
async function fetchCategoryData() {
    try {
        const response = await fetch('/api/categories');
        const categoryData = await response.json();
        
        if (categoryData.length > 0) {
            createCategoryChart(categoryData);
        } else {
            // Handle empty data
            const chartContainer = document.getElementById('category-chart');
            chartContainer.innerHTML = '<div class="flex h-full items-center justify-center text-gray-400">No category data available</div>';
        }
    } catch (error) {
        console.error('Error fetching category data:', error);
    }
}

// Create the category pie chart
function createCategoryChart(categoryData) {
    const ctx = document.getElementById('category-chart').getContext('2d');
    
    // Chart colors
    const colors = [
        'rgba(99, 102, 241, 0.8)',    // Indigo
        'rgba(16, 185, 129, 0.8)',    // Green
        'rgba(59, 130, 246, 0.8)',    // Blue
        'rgba(217, 70, 239, 0.8)',    // Purple
        'rgba(245, 158, 11, 0.8)',    // Yellow
        'rgba(239, 68, 68, 0.8)',     // Red
        'rgba(236, 72, 153, 0.8)',    // Pink
        'rgba(107, 114, 128, 0.8)'    // Gray
    ];
    
    // Prepare data for Chart.js
    const labels = categoryData.map(item => item.name);
    const values = categoryData.map(item => item.value);
    
    // Create chart
    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: values,
                backgroundColor: colors.slice(0, categoryData.length),
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'right',
                    labels: {
                        font: {
                            size: 12
                        },
                        padding: 15
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const label = context.label || '';
                            const value = context.raw.toFixed(2);
                            return `${label}: ₹${value}`;
                        }
                    }
                }
            },
            cutout: '70%'
        }
    });
}

// Initialize expense search functionality
function initSearch() {
    const searchInput = document.getElementById('search-expenses');
    
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            const query = this.value.toLowerCase();
            const rows = document.querySelectorAll('#expense-table-body tr');
            
            rows.forEach(row => {
                if (row.cells.length > 1) { // Skip empty state row
                    const date = row.cells[0].textContent.toLowerCase();
                    const description = row.cells[1].textContent.toLowerCase();
                    const category = row.cells[2].textContent.toLowerCase();
                    
                    if (date.includes(query) || description.includes(query) || category.includes(query)) {
                        row.style.display = '';
                    } else {
                        row.style.display = 'none';
                    }
                }
            });
        });
    }
} 