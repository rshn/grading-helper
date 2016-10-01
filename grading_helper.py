import glob
import os
import re
import sys
import argparse
import shutil

# Global Variables
default_pts_subtraction_per_comment = 0.2

# ################

class session:
  # These are the relevant methods to use the Update All function of Sakai.

  def __init__(self, bulk_path_string):
    self.bulk_path_string = os.path.realpath(bulk_path_string) # this is the path before bulk_download folder
    self.reports_list = [] # list of report objects, here each report is a nb file
    self.nb_files_path_string = os.path.join(self.bulk_path_string, 'nb_files')
    self.graded_path_string = os.path.join(self.bulk_path_string, 'graded')
    self.all_grades_path_string = self.bulk_path_string
    self.bulk_download_path_string = os.path.join(self.bulk_path_string, 'bulk_download')
    try:
      self.lab_bulk_path_string = os.path.join(self.bulk_download_path_string, next(os.walk(self.bulk_download_path_string))[1][0])
    except:
      print('Error 03: Check to see if you have the bulk_download folder, not the zip file, in this path:', self.bulk_path_string)
      sys.exit()
    print("The main path is: ", self.bulk_path_string)
    print("The nb_files folder is or will be at: ", self.nb_files_path_string)
    print("The graded folder containing the comments is or will be at: ", self.graded_path_string)
    print("The all_grades.txt is or will be at: ", self.all_grades_path_string)
    print("The bulk_download folder address: ", self.bulk_download_path_string)
    print("The lab folder containing students folders and grades.csv file is at: ", self.lab_bulk_path_string)
    print()

  def find_reports(self):
    # This function finds all the nb files and updates self.reports_list.
    self.reports_list = []
    path = self.bulk_path_string
    path_nb = self.nb_files_path_string

    try:
      os.chdir(path_nb)
      print('Finding reports inside the nb_files folder. Not copying anything.')
      print('If your nb_files folder is empty, delete the folder and run "grading_helper --mode nb" again. Be sure to have the bulk_download folder on the path.')
      result = []
      for root, dirs, files in os.walk(path_nb):
        for name in files:
          if '.nb' in name:
            result.append(os.path.join(root, name))

      for report_path in result:
        self.reports_list.append(report(report_path))

    except:
      print('Found reports in the lab folder and copied them to nb_files folder. Makes grading easier.')
      result = []
      for root, dirs, files in os.walk(path):
        for name in files:
          if '.nb' in name:
            result.append(os.path.join(root, name))
      
      os.chdir(path)
      os.mkdir('nb_files')
      os.chdir(path_nb)

      for report_path in result:
        shutil.copy2(report_path, path_nb)
        new_path = path_nb + os.path.basename(report_path)
        self.reports_list.append(report(new_path))

  def copy_back_nb_files_sakai(self):
    # This function copies back the graded nb files with comments.
    # It removes the notebook files from the bulk_download folder.
    # Then copies the commented version inside nb_files folder.
    # Use with caution!
    lab_path = self.lab_bulk_path_string
    nb_files_path = self.nb_files_path_string

    labs_nb = []
    for root, dirs, files in os.walk(lab_path):
      for name in files:
        if '.nb' in name:
          labs_nb.append(os.path.join(root, name))
    nb_files = []
    for root, dirs, files in os.walk(nb_files_path):
      for name in files:
        if '.nb' in name:
          nb_files.append(os.path.join(root, name))
    
    # Remove and replace the notebook files in the lab folder with the graded ones in the nb_files folder.
    for lab_nb in labs_nb:
      os.remove(lab_nb)
      lab_filename = os.path.basename(lab_nb)
      for nb_file in nb_files:
        nb_filename = os.path.basename(nb_file)
        if (lab_filename == nb_filename):
          shutil.copyfile(nb_file, lab_nb)
      

  def grade_reports(self):
    for report in self.reports_list:
      report.write_graded()
    self.write_all_grades_txt() 

  def write_all_grades_txt(self):
    path = os.path.join(self.all_grades_path_string, 'all_grades.txt')
    agrf = open(path, 'w')
    for report in self.reports_list:
      for name in report.info_dict['names_list']:
        agrf.write(name + '\t' + '%.1f' % round(report.grade_float, 1) + '\n')
    agrf.close()


  def update_comments_txt_sakai(self):
    # This function updates the comments.txt file in student folder in Sakai bulk_download folder structure.
    graded_path = self.graded_path_string # path to the txt files containing feedbacks
    lab_path = self.lab_bulk_path_string

    lab_report_list = next(os.walk(graded_path))[2]
    folder_list = next(os.walk(lab_path))[1]

    f_filled = [];
    lr_placed = [];
    for lr in lab_report_list:
        name = os.path.splitext(os.path.basename(lr))[0];
        name = name.split('_');
        match_found = 0
        for f in folder_list:
          if all(n.upper() in f.upper() for n in name):
            try:
              os.remove(os.path.join(lab_path, f, 'comments.txt'));
            except:
              print(os.path.join(lab_path, f, 'comments.txt'), 'is already removed.')

            shutil.copyfile(os.path.join(graded_path, lr), os.path.join(lab_path, f,'comments.txt'));
            f_filled.append(f);
            lr_placed.append(lr);
            match_found = 1
        # If there are mismatches in the names, will try only the family name.
        if not match_found:
          # If the first name and family name not matched, we will try only family name.
          print('>> There is a name mismatch when trying to copy the comments.txt for,')
          print(lr)
          print('>> Will try only the last name. Usually this is a nickname issue. But when grading check the "Names:" line.')
 
          for f in folder_list:
            if (name[1].upper() in f.upper()):
              try:
                os.remove(os.path.join(lab_path, f, 'comments.txt'));
              except:
                print(os.path.join(lab_path, f, 'comments.txt'), 'is already removed.')

              shutil.copyfile(os.path.join(graded_path, lr), os.path.join(lab_path, f,'comments.txt'));
              f_filled.append(f);
              lr_placed.append(lr);
              match_found = 1
              print('>> Matched with last name!\n')

        if not match_found:
          print('!! Problem occurred when processing these names/grades from all_grades.txt when putting in grades.csv: ')
          print('!! ' + name)
          print('!! This might be caused by the students not putting their names properly in the "Names: " line of the report.')

    if len(f_filled) != len(folder_list):
      print('!! The comment were not placed for the following folders (probably "Names: " line issue in nb file):')
      print('!! ', set(folder_list)-set(f_filled))
    if len(lr_placed) != len(lab_report_list):
      print('!! The following comment were not placed in folders (probably "Names: " line issue in nb file):')
      print('!! ', set(lab_report_list)-set(lr_placed), '\n')


  def update_grades_csv_sakai(self):
    # This function updates the grades.csv file in the bulk_download folder structure in Sakai.
    csv_path = self.lab_bulk_path_string
    os.rename(os.path.join(csv_path,'grades.csv'), os.path.join(csv_path,'blank.csv'))

    blkf = open(os.path.join(csv_path, 'blank.csv'), 'r');
    csvf = open(os.path.join(csv_path, 'grades.csv'), 'w');
    
    grades_path = self.all_grades_path_string 
    grdf = open(os.path.join(grades_path, 'all_grades.txt'), 'r');
    fst_names = [];
    lst_names = [];
    grades = []
    # This for loop gets the first and last name and grades.
    for line in grdf:
        temp = line.split('\t');
        name = temp[0];
        name = name.split(' ');
        grades.append(temp[1].replace('\n',''));
        fst_names.append(name[0]);
        lst_names.append(name[1]);
    grdf.close()

    flag = 0;
    for line in blkf:
      line_list = line.split(',')
      if (flag == 0):
        csvf.write(line);
        if 'Display ID' in line:
          flag = 1
          f_name_col = line_list.index('"First Name"') 
          l_name_col = line_list.index('"Last Name"')
          grade_col = line_list.index('"grade"')
      else:
        match_found = 0
        for i in range(0,len(fst_names)):
          if ((fst_names[i].upper() in line.upper()) and (lst_names[i].upper() in line.upper())):
            line_list[grade_col] = '"' + grades[i] + '"'
            new_line = ','.join(line_list)
            csvf.write(new_line);
            # fst_name[i] and last_name[i] and grade[i] already matched, so remove them from lists.
            #del fst_names[i]
            #del lst_names[i]
            #del grades[i]
            match_found = 1
        if match_found == 0:
          # If the first name and family name not matched, we will try only family name.
          print('>> There is a name mismatch in this grades.csv name,')
          print('>> ' + 'First Name: ' + line_list[f_name_col] + ', Last Name: ' + line_list[l_name_col])
          print('>> Will try only the last name. Usually this is a nickname issue. But when grading check the "Names:" line.')
          for i in range(0,len(fst_names)):
            if (lst_names[i].upper() in line.upper()):
              line_list[grade_col] = '"' + grades[i] + '"'
              new_line = ','.join(line_list)
              csvf.write(new_line);
              # fst_name[i] and last_name[i] and grade[i] already matched, so remove them from lists.
              #del fst_names[i]
              #del lst_names[i]
              #del grades[i]
              match_found = 1
              print('>> Matched with last name!\n')
        # if still not matched
        if match_found == 0:
          print('!! Problem occurred when processing these names/grades from all_grades.txt when putting in grades.csv: ')
          print('!! ' + fst_names, lst_names, grades)
          print('!! This might be caused by the students not putting their names properly in the "Names: " line of the report.\n')

    blkf.close();
    csvf.close();
    os.remove(os.path.join(csv_path, 'blank.csv'))

    

class report:
  def __init__(self, path_string):
    self.path_string = path_string
    self.info_dict = {} # names_list, names_string, section_string, date_string
    self.comments_list = [] # list of comment objects
    self.grade_float = 10.0

  # These are the methods
  #   gather_info(self)
  #   gather_comments(self)
  #   write_graded(self)
  #   update_grade(self)

  def gather_info(self):
    # This function gathers the info, i.e. names, section, and date.
    # Do not mistake with get/set.
    # It will update self.info_dict.

    f = open(self.path_string, 'r');
    nb_file_name = os.path.basename(self.path_string);

    # The names after 'Names:' must be comma searated
    for line in f:
      if ('Names:' in line):
        line = line.replace(r' and ', r', ')
        line = line.replace(r' & ', r', ')
        names_list = re.split(r',', line)
        names_list[0] = names_list[0].split(r': ')[1]
        for idx, name in enumerate(names_list):
          names_list[idx] = name.strip()
        names_string = ', '.join(names_list)
  
      if ('Section:' in line):
        m = re.search(r'Section:\s*(\w+)', line);
        if m:
          section_string =  m.group(1);
        else:
          section_string = "not_found_section_" + nb_file_name;

      if ('Date:' in line):
        m = re.search(r'Date:\s*(.+)\\', line);
        if m:
          date_string = m.group(1);
        else:
          date_string = "not_found_date_" + nb_file_name;

    self.info_dict = {'names_list': names_list, 'names_string': names_string, 'section_string': section_string, 'date_string': date_string}
    f.close()

  def gather_comments(self):
    # This function gathers comments in the report and updates self.comments_list.
    
    self.comments_list = []

    f = open(self.path_string, 'r');
    nb_file_name = os.path.basename(self.path_string);

    f.seek(0);
    lines = f.read();

    # grab position of "Part" in mathmatica note book
    part_name_list = [m.group() for m in re.finditer(r'(?<! )Part\s[\s-]*[IV]+', lines)]
    part_start_idx_list = [m.start() for m in re.finditer(r'(?<! )Part\s[\s-]*[IV]+', lines)]

    # grab positions where comments starts(<cm>) and ends(</cm>)
    cm_start_idx_list = [m.end() for m in re.finditer('<cm>', lines)]
    cm_end_idx_list = [m.start() for m in re.finditer('</cm>', lines)]
 
    # grab positions of the questions/steps in mathmatica notebook
    question_start_idx_list = [m.start() for m in re.finditer(r'Question\s*\d', lines)];    
    step_start_idx_list = [m.start() for m in re.finditer(r'Step\s*\d', lines)];

    qs_start_idx_list = question_start_idx_list + step_start_idx_list;
    qs_start_idx_list.sort();
    
    # get individual comments (first check if <cm> and </cm> is in pairs)        
    if (len(cm_start_idx_list) != len(cm_end_idx_list)):
      print(self.path_string)
      print("Error 01: Different number of <cm> tag(s) and </cm> tags in the document.")
      print("Error 01: Can not process instructor comments correctly!")
      sys.exit()
    else:
      idx_diff = [y - x for x, y in zip(cm_start_idx_list, cm_end_idx_list)]
      if any(idx_diff_i < 0 for idx_diff_i in idx_diff):
        print(self.path_string)
        print("Error 02: <cm> tags and </cm> tags mismatch.")
        print("Error 02: Can not process instructor comments correctly!")
        sys.exit()

    # If the functions gets here, it means the <cm></cm> tags are used correctly.
    # So we process them and update the self.comments_list.
    # if <cm> and </cm> tags are paired correctly, process comments
    for i in range(0, len(cm_start_idx_list)):
      # check which question the comment is associated with
      qs_start_idx_list.append(len(lines));
      qs_start_idx_idx = next(index for index,value in enumerate(qs_start_idx_list) if value > cm_start_idx_list[i])-1;
      c_qs_start_idx = qs_start_idx_list[qs_start_idx_idx];
      # grab Question/Step number
      m = re.search(r'Question\s*\d|Step\s*\d',lines[c_qs_start_idx:cm_start_idx_list[i]]);
      if m:
        qs_id = m.group(0);
      else:
        qs_id = '';
      # check which part the question belongs to
      part_start_idx_list.append(len(lines));
      c_part_idx_idx = next(index for index,value in enumerate(part_start_idx_list) if value > cm_start_idx_list[i])-1;
      # grab Part name
      if part_name_list: 
        c_part_name = part_name_list[c_part_idx_idx]

      # Now we save the comment at the end of the self.comments_list.
      cm_string = lines[cm_start_idx_list[i]:cm_end_idx_list[i]]
      cm_meta_dict = {'number': i+1, 'part': c_part_name, 'qs': qs_id} 
      self.comments_list.append(comment(self, cm_meta_dict, cm_string))

      

    f.close()


  def write_graded(self):
    # This function calls other functions to gather the info and comments and to update the grade,
    # and then writes a txt file inside 'graded' folder.
    # A separate file for each student.
    self.gather_info()
    self.gather_comments()
    self.update_grade()
    # round in 0.1 interval
    # self.grade_float = round(self.grade_float/0.1)*0.1

    lab_report_feedback = '';
    lab_report_feedback += "Names: " + self.info_dict['names_string'] + '\n'
    lab_report_feedback += "Lab Date: " + self.info_dict['date_string'] + '\n'
    lab_report_feedback += "Section: " + self.info_dict['section_string'] + '\n'
    lab_report_feedback += "==== Comments for the Lab Report ====" + '\n'
    for comment in self.comments_list:
      lab_report_feedback += comment.meta_string()
    
    lab_report_feedback += "==== Grade: " + '%.1f' %round(self.grade_float, 1) + " ====\n"
    lab_report_feedback += "Total # of comments: " + str(len(self.comments_list)) + '\n' 

    graded_folder_path = os.path.join(os.path.realpath('..'),'graded') 
    try:
      os.chdir(graded_folder_path)
    except:
      os.mkdir(graded_folder_path)

    for name in self.info_dict['names_list']:
      cm_file_name = name.replace(' ','_') + '.txt'
      f = open(os.path.join(graded_folder_path, cm_file_name), 'w')
      f.write(lab_report_feedback)
      f.close()

  def update_grade(self):
    grade = 10.0
    for comment in self.comments_list:
      grade -= comment.pts_float
    self.grade_float = grade


class comment:
  def __init__(self, report, meta_dict, cm_string):
    self.report = report # This is the report where the comment comes from.
    self.meta_dict = meta_dict # meta_dict has the information where the comment sits inside the report.
    self.cm_string = cm_string # This is the content of the comment <cm>cm_string</cm>.
    self.pts_float = default_pts_subtraction_per_comment # This is the points lost because of the comment.
    self.clean_up()
    self.update_pts()
    # It updates if given inside brackets in cm_string.

  def clean_up(self):
    # This function cleans up the raw comment.
    
    raw_cm = self.cm_string
    
    # replace mathmatica symbols in the comment
    symbol_dict = {r'\[Dash]':r'-',
                   r'\[OpenCurlyDoubleQuote]':r'"',
                   r'\[CloseCurlyDoubleQuote]':r'"',
                   r'\[OpenCurlyQuote]':r"'",
                   r'\[CloseCurlyQuote]':r"'"};
    for k, v in symbol_dict.items():
      if (k in raw_cm):
        raw_cm = raw_cm.replace(k,v);

    # kill "\" (Mathmatica line breaks) in comment.
    raw_cm = raw_cm.replace(r'\[','backslash-bracket');                   
    raw_cm = raw_cm.replace('\\',r'');
    raw_cm = raw_cm.replace('backslash-bracket',r'\[');

    # kill line breaks in comment.
    raw_cm = raw_cm.replace('\n',r'');
    raw_cm = raw_cm.replace('\r',r'');

    self.cm_string = raw_cm

  def update_pts(self):
    # This function processes the cm_string and finds [] tags inside the comment.
    # [] tag is used for grading. For example '[0.3] Blah Blah' means 0.3 points lost.
    # It updates pts_float.
    
    # Get pts tags which are in [] and not preceeded by \
    pts_tag = re.findall(r'(?<!\\)\[(.+?)\]', self.cm_string);
    if pts_tag:
      try:
        self.pts_float = float(pts_tag[0])
      except:
        print(self.report.path_string)
        print(self.cm_string)
        print(pts_tag)
        print('The pts tag is not a number. Use brackets [] only once in each comment \
              with a number inside brackets. For example, <cm>[0.5] Your comment.</cm>.')
    else:
      print(self.report.path_string)
      print(self.cm_string)
      print('No pts is given. So this comment will reduce default value per comment, which is %.1f.' %(self.pts_float))

  def meta_string(self):
    # This function writes the meta information of the comment properly and returns it as a string.
    if self.meta_dict['part']:
      meta_string = "Comment " + str(self.meta_dict['number']) + " | " + self.meta_dict['part'] + ' : ' + self.meta_dict['qs'] + " | " + self.cm_string + '\n'
    else:
      meta_string = "Comment " + str(self.meta_dict['number']) + " | " + self.meta_dict['qs'] + " | " + self.cm_string + '\n'

    return meta_string

def main():
  args_list = sys.argv[1:]
  parser = argparse.ArgumentParser(description = 'Helping you to grade the notebook files. \
                                   You only need to put your comments in the nb file in the format \
                                   <cm>[points to be subtracted out of 10] Your comment.</cm> \
                                   and this code takes care of everything else. \
                                   To use it, first run it with --mode nb which will give you the notebook files inside nb_files folder. \
                                   Then put the comments on the notebook files inside the nb_files folder. \
                                   Now run the code with --mode gr which grades and makes graded folder with comments and all_grades.txt file. \
                                   Check to see if everything looks good. Also change the alias names to Sakai names for the students. \
                                   If everything looks good, do the final run with --mode up. This will update the bulk_download folder. \
                                   Now make a zip archive file using the folder inside the bulk_download, and use Upload All on the Sakai page.')
  parser.add_argument('--mode', default = 'gr', choices = ['nb', 'gr', 'up'], \
                      help = 'There are three modes, nb, gr, and up. \
                      nb mode finds all the nb files and saves them inside a folder named nb_files. \
                      This makes it easier to grade. \
                      gr mode finds all the comments in nb files and calculate things and put result in files. \
                      up mode, which must be used with caution, will update the Sakai folder system with the grades and comments. \
                      You only need to make a zip file and use Upload All functionality of Sakai.')
  parser.add_argument('--path', default = './', help = 'The folder to grab the nb files from, or update the bulk_download folder for Sakai.')

  parsed = parser.parse_args(args_list)
  mode = parsed.mode
  path = parsed.path

  try:
    os.chdir(path)
  except:
    print('The path given not found. Using the current directory as the path.')
    path = './'

  this_session = session(path)

  if mode == 'nb':
    print('nb mode: only finding the nb files and putting them in the nb_files folder so it is easier to grade.\n')
    this_session.find_reports()
    sys.exit()
  elif mode == 'gr':
    print('gr mode: will get the comments and calculate the grades, will save them in comment files inside graded folder and all_grades.txt file.\n')
    this_session.find_reports()
    this_session.grade_reports()
  elif mode == 'up':
    print('up mode: will use the comment files inside graded folder and all_grades.txt file to update the bulk_download folder,\
          \ncopying the nb files, updating comments.txt files, and grades.csv file.\n')
    this_session.update_comments_txt_sakai()
    this_session.update_grades_csv_sakai()
    this_session.copy_back_nb_files_sakai()


if __name__ == "__main__":
  main()


