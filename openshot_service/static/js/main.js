document.addEventListener('DOMContentLoaded', function() {
    // Check OpenShot availability
    fetch('/health')
        .then(response => response.json())
        .then(data => {
            const openShotStatus = document.getElementById('openshot-status');
            if (data.openshot_available) {
                openShotStatus.textContent = 'Available';
                openShotStatus.style.backgroundColor = '#27ae60'; // Green
            } else {
                openShotStatus.textContent = 'Not Available';
                openShotStatus.style.backgroundColor = '#e74c3c'; // Red
            }
        })
        .catch(error => {
            console.error('Error fetching health status:', error);
            const openShotStatus = document.getElementById('openshot-status');
            openShotStatus.textContent = 'Error';
            openShotStatus.style.backgroundColor = '#e74c3c'; // Red
        });

    // Show API documentation when button is clicked
    const showDocsBtn = document.getElementById('show-docs-btn');
    showDocsBtn.addEventListener('click', function() {
        alert('API documentation is not available in this demo. Check the console for endpoint details.');
        
        // Log API documentation to console for developers
        console.log('OpenShot Processing Service API');
        console.log('---------------------------------');
        console.log('POST /login - Authenticate User');
        console.log('Request: { "username": "string", "password": "string" }');
        console.log('Response: { "message": "string", "user_id": number }');
        console.log('---------------------------------');
        console.log('POST /register - Register New User');
        console.log('Request: { "username": "string", "password": "string", "email": "string" }');
        console.log('Response: { "message": "string" }');
        console.log('---------------------------------');
        console.log('POST /submit-job - Submit Processing Job');
        console.log('Request: { "job_type": "string", "parameters": object }');
        console.log('Response: { "message": "string", "job_id": number, "status": "string" }');
        console.log('---------------------------------');
        console.log('GET /job/{job_id} - Get Job Status');
        console.log('Response: { "job_id": number, "job_type": "string", "status": "string", "created_at": "string", "updated_at": "string", "result": "string" }');
        console.log('---------------------------------');
        console.log('GET /user/jobs - List User Jobs');
        console.log('Response: { "jobs": array }');
    });
});