<h1>This repository is a personal project that I've developed over <em>3 months</em>.</h1>
<p>It really helped me understand <strong>Django</strong> and the <strong>MVC design pattern</strong>.</p>

<h2>Project Setup</h2>
<ul>
    <li><strong>proyecto:</strong> Main project directory.</li>
    <li><strong>website:</strong> Main application of the project.</li>
    <li><strong>media:</strong> Directory for storing media files.</li>
    <li><strong>static:</strong> Directory for static files such as CSS, JavaScript, and images.</li>
</ul>

<h2>Core Technologies</h2>
<p><strong>Django</strong></p>
<p><strong>Django</strong> is a <em>Python web framework</em> that facilitates rapid and clean development of web applications. In this project, it is used to manage the project structure, handle the database, and facilitate the creation of views and URLs.</p>

<p><strong>Django Rest Framework (DRF)</strong></p>
<p><strong>DRF</strong> is used to build <em>RESTful APIs</em> in the Django application. It makes it easy to create RESTful web services by providing a set of tools and conventions.</p>

<p><strong>DRF Spectacular</strong></p>
<p><strong>DRF Spectacular</strong> is used for automatic generation of <em>API documentation</em>. This improves understanding and collaboration by providing an interactive interface to explore API endpoints.</p>

<p><strong>MySQL</strong></p>
<p>The <strong>MySQL</strong> database management system is configured as the default database for this project.</p>

<p><strong>Google Maps API</strong></p>
<p><strong>Google Maps API</strong> is integrated using the provided API key.</p>

<h2>Important Configurations</h2>
<ul>
    <li><strong>SECRET_KEY:</strong> Secret key for application security.</li>
    <li><strong>DEBUG:</strong> Debug mode enabled (not to be used in production environments).</li>
    <li><strong>ALLOWED_HOSTS:</strong> List of allowed hosts for the application.</li>
    <li><strong>INSTALLED_APPS:</strong> List of installed applications, including Django Admin, authentication, and the custom "website" application.</li>
    <li><strong>DATABASES:</strong> MySQL database configuration.</li>
    <li><strong>STATIC_URL:</strong> URL for static files.</li>
    <li><strong>MEDIA_ROOT and MEDIA_URL:</strong> Configuration for handling media files.</li>
</ul>

<h2>Email Configuration</h2>
<p>SMTP email backend is used for sending emails. Configuration includes details such as the <strong>Gmail SMTP server</strong>, <strong>port</strong>, and <strong>user credentials</strong>.</p>

<h2>REST Framework Configuration</h2>
<p><strong>DRF Spectacular's</strong> automatic schema is used for <em>API documentation</em>. Default permission is set to <strong>allow any</strong>.</p>
