# grading-helper
A Python script to get the comments like  
`<cm>[points to be subtracted out of 10.0] The comments you write.</cm>`  
out of a text format file and calculate the grades and update everything for Sakai's folder system.

How to use this code:

1) The only thing you need so you can use this program is to have Python (2.x or 3.x) installed on your computer.
2) When you want to grade follow these steps,

**Step 1.** Go to the Assignment in Sakai and click on Download All which will give you a bulk_download.zip file.  
**Step 2.** Put this file in some path in your computer, will be called 'main path'.  
**Step 3.** Unzip the bulk_download.zip to make a bulk_download folder in the 'main path'. Inside the bulk_download folder, there is 'the lab folder'.  
          If a student have put the wrong pre-lab nb file in lab submission, delete this nb file from 'the lab folder'.  
**Step 4.** Copy grading_helper.py in the 'main path' (or use `--path 'main path'` argument when running the code).  
**Step 5.** Run the code in the nb mode, i.e. use a terminal (or command prompt) to run,
```
  python grading_helper.py --mode nb
```
This will look for all the nb files inside the bulk_download folder and copy them in one place, nb_files folder in 'main path'. This makes grading easier.  
**Step 6.** Now it is time to start grading. Go to nb_files folder and open the nb file you want to grade and check 'Names: ' line, so it is not missing any names.  
**Step 7.** Put your comments inside the nb file, at the appropriate spot, using this format,  
`<cm>[pts to subtract out of 10.0] Your comment.</cm>`  
For example,  
`<cm>[0.3] You have used wrong number of significant figures. Match them between the number and its error.</cm>`  
Do not forget to close the `<cm>` tag with `</cm>`. The grading_helper.py is really unforgiving when it comes to tags, unlike html.  
If you do not use [0.3] on above example, the default default_pts_subtraction_per_comment will apply which I set to 0.2 in the grading_helper.py.
You can change it if you like.  
Only use brackets [] for grading purposes, like above, and inside cm tag.
I mean, do not use brackets [] for anything else. If this would bother you let me know.  
**Step 8.** Now that you put your comments, at the appropriate spots, run,
```
python grading_helper.py --mode gr
```
This will grade all the nb files inside the nb_files folder and will make graded folder and all_grades.txt file in 'main path'.  
**Step 9.** Check all_grades.txt file and graded folder and see if things look good. Please contact me if they don't.  
**Step 10.** Now run,
```
python grading_helper.py --mode up
```
This will update all the comments.txt files and grades.csv file inside bulk_download folder.  
**Step 11.** Now make a zip file using 'the lab folder'. Do not zip the bulk_download folder. It won't work with Sakai.  
**Step 12.** Now go to the assignment on Sakai and click on Upload All and choose the zip file you made. You are done putting everything in place.
