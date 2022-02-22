# Panorama - API

## Contents:

<!--ts-->
   * [About](#about)
   * [Functionalities](#functionalities)
   * [Requisites](#requisites)
   * [How to Use](#how-to-use)
<!--te-->

About
============

API Panorama Project searches through IP's and returns System and License data from Firewalls.

Functionalities
============
- Reading IP's listing;
- At each API request a new API key is automatically generated;
- Get the Data and add it to an XLSX file;
- URL or port not found error handling:
If a URL or PORT is wrong, it will generate the text file "error_panorama.log" which will be in the same directory as the Python Script.
Example Error log: 2022-01-22 19:33:34 WARNING URL Panorama Failed: https://111.222.333.54:444" (the port 3 is missing);
- Excel file formatting:
Table Formatting, Table Name (Firewall): "Firewall" and Sheet Name "PanoramaFirewalls";
Table Formatting, Table Name (Licenses): "Licenses" and Sheet Name "PanoramaLicens".

Requisites
============
- Must have a registered user on each Panorama with "Superuser" permission and XML/API;

How To Use
============
- Insert the IP listing of the Panorama in the "ip_list_panorama.txt" file;
- Insert the username and password with "Superuser" and (MXL/API) permissions in "main.py";
- Execute the Script to generate .xlsx file to Firewall Info and Licenses.







