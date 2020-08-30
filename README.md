# Water quality parsing and mapping
 Personal project to pull Santa Barbara County ocean water quality information from report PDFs posted to county website and post to AWS RDS. 
 
The Santa Barbara County Health department samples at least weekly, often more frequently if a beach exceeds state health standards or isn't tested in the first batch of tests, then posts the results online to their website. The link is static as the file name never changes, just the contents of the PDF.

This requires the script to be ran daily in which the PDF is downloaded, contents hashed, and checked against previously hashed PDFs. If the PDF is new, then the contents are parsed and information, including hash, are added to a Postgres AWS RDS. Logic is then used to determine if the PDF is for a new week or ammends the results of a previously PDF. Ammendments occurr when a beach is re-sampled or if there were beaches not yet tested when the initial PDF was released. 

If an ammendment occurred, then just the ammended information is added to the water quality water DB table. 

Currently this script is running on my local machine as a scheduled task.

##TODO:
Implement scheduling in Flask so that this task can be ran on my AWS EB site. 
