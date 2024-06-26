// static/assets/js/report.js


function printTable() {
    console.log("Printing table...");
    window.print();
}


document.addEventListener('DOMContentLoaded', function () {

    document.getElementById('exportButton').addEventListener('click', function() {
        document.querySelector('.dt-buttons').classList.toggle('show');
    });

    document.addEventListener('click', function(event) {
        var isClickInside = document.querySelector('.dt-buttons').contains(event.target);

        if (!isClickInside) {
            document.querySelector('.dt-buttons').classList.remove('show');
        }
    });
});

