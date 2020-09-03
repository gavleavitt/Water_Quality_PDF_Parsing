# Water quality parsing and mapping
Personal project to pull Santa Barbara County ocean water quality information from PDFs posted to the county Health Department website and insert details into personal PostGres AWS RDS. 
 
The Santa Barbara County Health department samples at least weekly, often more frequently if a beach exceeds state health standards or isn't tested in the first batch of tests, then posts the results online to their website. The link is static as the file name never changes, just the contents of the PDF.

Santa Barbara County Ocean Water Monitoring Program webpage: https://www.countyofsb.org/phd/oceanwatermonitoring/

Test results PDF download link posted to the program webpage: https://www.countyofsb.org/uploadedFiles/phd/PROGRAMS/EHS/Ocean%20Water%20Weekly%20Results.pdf

This requires the script to be ran daily in which the PDF is downloaded, contents hashed, and checked against previously hashed PDFs. If the PDF is new, then the contents are parsed and information, including hash, are added to a Postgres AWS RDS. Logic is then used to determine if the PDF is for a new week or ammends the results of a previously PDF. Ammendments occurr when a beach is re-sampled or if there were beaches not yet tested when the initial PDF was released. 

If an ammendment occurred, then just the ammended information is added to the water quality water DB table. 

Currently this script is running on my local machine as a scheduled task.

##TODO:
Implement scheduling in Flask so that this script can be integrated into my Flask Website as a scheduled task. 
