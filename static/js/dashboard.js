// Admin & User Dashboard Analytics with Chart.js
document.addEventListener('DOMContentLoaded', function () {
  // 1. Category Distribution Chart (Doughnut)
  const categoryCanvas = document.getElementById('categoryChart');
  if (categoryCanvas) {
    const categoriesDataRaw = categoryCanvas.getAttribute('data-categories');
    let categoriesObj = {};
    try {
      categoriesObj = JSON.parse(categoriesDataRaw);
    } catch (e) {
      categoriesObj = {
        'Mobile Phones': 4,
        'Laptops': 3,
        'Computers': 2,
        'Batteries': 8,
        'Chargers': 5,
        'Televisions': 2,
        'Other Electronics': 1
      };
    }

    const labels = Object.keys(categoriesObj);
    const dataValues = Object.values(categoriesObj);

    new Chart(categoryCanvas, {
      type: 'doughnut',
      data: {
        labels: labels.length ? labels : ['No Items'],
        datasets: [{
          data: dataValues.length ? dataValues : [1],
          backgroundColor: [
            '#198754', // Green
            '#0d6efd', // Blue
            '#20c997', // Teal
            '#ffc107', // Amber
            '#fd7e14', // Orange
            '#6f42c1', // Purple
            '#6c757d'  // Gray
          ],
          borderWidth: 2,
          borderColor: '#ffffff'
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'bottom',
            labels: {
              boxWidth: 12,
              padding: 15,
              font: { size: 12 }
            }
          },
          tooltip: {
            callbacks: {
              label: function (context) {
                return ` ${context.label}: ${context.raw} items`;
              }
            }
          }
        },
        cutout: '65%'
      }
    });
  }

  // 2. Request Status Chart (Bar)
  const statusCanvas = document.getElementById('statusChart');
  if (statusCanvas) {
    const pending = parseInt(statusCanvas.getAttribute('data-pending') || '0', 10);
    const approved = parseInt(statusCanvas.getAttribute('data-approved') || '0', 10);
    const inProgress = parseInt(statusCanvas.getAttribute('data-inprogress') || '0', 10);
    const completed = parseInt(statusCanvas.getAttribute('data-completed') || '0', 10);
    const rejected = parseInt(statusCanvas.getAttribute('data-rejected') || '0', 10);

    new Chart(statusCanvas, {
      type: 'bar',
      data: {
        labels: ['Pending', 'Approved', 'In Progress', 'Completed', 'Rejected'],
        datasets: [{
          label: 'Collection Requests',
          data: [pending, approved, inProgress, completed, rejected],
          backgroundColor: [
            'rgba(255, 193, 7, 0.85)',   // Warning Yellow
            'rgba(13, 110, 253, 0.85)',  // Primary Blue
            'rgba(13, 202, 240, 0.85)',  // Cyan
            'rgba(25, 135, 84, 0.85)',   // Eco Green
            'rgba(220, 53, 69, 0.85)'    // Danger Red
          ],
          borderColor: [
            '#ffc107',
            '#0d6efd',
            '#0dcaf0',
            '#198754',
            '#dc3545'
          ],
          borderWidth: 1,
          borderRadius: 6
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false }
        },
        scales: {
          y: {
            beginAtZero: true,
            ticks: {
              precision: 0,
              font: { size: 12 }
            },
            grid: {
              color: '#f1f5f9'
            }
          },
          x: {
            grid: { display: false }
          }
        }
      }
    });
  }

  // 3. Item Condition Breakdown (Pie)
  const conditionCanvas = document.getElementById('conditionChart');
  if (conditionCanvas) {
    const condDataRaw = conditionCanvas.getAttribute('data-conditions');
    let condObj = {};
    try {
      condObj = JSON.parse(condDataRaw);
    } catch (e) {
      condObj = { 'Working': 1, 'Damaged': 2, 'Not Working': 5 };
    }

    new Chart(conditionCanvas, {
      type: 'pie',
      data: {
        labels: Object.keys(condObj),
        datasets: [{
          data: Object.values(condObj),
          backgroundColor: [
            '#198754', // Working (Green)
            '#fd7e14', // Damaged (Orange)
            '#dc3545'  // Not Working (Red)
          ],
          borderColor: '#ffffff',
          borderWidth: 2
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'bottom',
            labels: { boxWidth: 12, padding: 12 }
          }
        }
      }
    });
  }

  // 4. Number Counter Animation
  const counters = document.querySelectorAll('.counter-anim');
  counters.forEach(counter => {
    const target = +counter.getAttribute('data-target');
    const duration = 1200; // ms
    const stepTime = 30;
    const steps = duration / stepTime;
    const increment = target / steps;
    let current = 0;

    const timer = setInterval(() => {
      current += increment;
      if (current >= target) {
        counter.textContent = target;
        clearInterval(timer);
      } else {
        counter.textContent = Math.ceil(current);
      }
    }, stepTime);
  });
});

