import os, sys, threading, json, shutil, base64, requests, io, traceback, html, shlex, math, hashlib

from math import ceil, log
from flask import Flask, request, Response, redirect
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

from threading import Thread
from subprocess import *

from time import time
import subprocess

import logging

debug = "--debug" in sys.argv

if not debug: logging.getLogger("werkzeug").setLevel(logging.ERROR)

users = json.loads(open("files/users.json").read())

def update_probs():
  return {p: json.loads(open("files/problems/%s/problem.json"%p).read()) for p in open("files/contest.txt").read().splitlines()}

def lessons():
  return json.loads(open("files/learn/lessons.json").read())

problem_map = update_probs()

pages = math.ceil(len(problem_map)/10)

running = eval(open("files/running.txt", "r").read().strip())

sudoers = open("files/admin.txt").read().splitlines()

extraTLS = {
  "Python 3.6.4": 4,
  "Python 2.7.6": 4,
  "Java 9.0.4": 2,
  "C++ (g++) 4.8.4": 1,
  "C (gcc) 4.8.4": 1,
  "Ruby 2.5.0": 4,
  "Ruby 1.9.3p484": 4,
  "Haskell (GHC 7.6.3)": 4,
  "COBOL (OpenCOBOL 1.1.0)": 4,
  "Kotlin 1.2.30 (SUPER SLOW)": 5
}

def grade(command, tests, cwd, language):
  for suite_num, subtask in enumerate(tests):
    points = subtask["points"]
    tasks = subtask["tests"]
    timelimit = subtask["timelimit"] * extraTLS[language]
    yield (0, points)
    skip = False
    for test_num, (i, o, key) in enumerate(tasks):
      i = decompress(i,key)
      if skip:
        yield (5,)
      else:
        start = time()
        try:
          expected = o.strip()
          actual = hashlib.sha384(check_output(command, cwd = cwd, input = bytes(i, "utf8"), stderr = sys.stdout, timeout = timelimit).strip()).hexdigest()
          if expected == actual:
            yield (1, time() - start)
          else:
            yield (2, time() - start, expected, actual); skip = True
        except subprocess.TimeoutExpired:
          yield (3, time() - start); skip = True
        except:
          traceback.print_exc()
          yield (4, time() - start); skip = True
    yield (6, (1 - skip) * points)
  yield (7,)

def flatten(gen):
  while True:
    yield from next(gen)

def test(command, tests, cwd, output = print, user = None, problem = "", language = ""):
  debug = "--debug" in sys.argv
  grader = flatten(grade(command, tests, cwd, language))
  total = 0
  while True:
    num = next(grader)
    if num == 0:
      points = next(grader)
      output(0)
      output(points)
      while True:
        id = next(grader)
        if id == 1: output(1); output(round(next(grader), 2))
        if id == 2: output(2); output(round(next(grader), 2))
        if id == 3: output(3); output(round(next(grader), 2))
        if id == 4: output(4); output(round(next(grader), 2))
        if id == 5: output(5)
        if id == 6: total += next(grader); break
    if num == 7:
      break
  if user:
    if user not in users:
      users[user] = {"scores": {}, "recency": time()}
    if total > users[user]["scores"].get(problem, 0):
      users[user]["scores"][problem] = total
      users[user]["recency"] = time()
    update_users()
  output(6)
  output(total)
  output(sum(subtask["points"] for subtask in tests))

def do_tests(array, command, tests):
  def function():
    gen = grade(command, tests)
    while True:
      try:
        array.append(next(gen))
      except StopIteration:
        break
  return function

name_to_command = {
  "Python 3.6.4": ["python3.6 Main.py"],
  "Python 2.7.6": ["python2 Main.py"],
  "Java 9.0.4": ["javac Main.java", "java Main"],
  "C++ (g++) 4.8.4": ["g++ -std=c++11 Main.cpp -o a.out", "./a.out"],
  "C (gcc) 4.8.4": ["gcc Main.c -o a.out","./a.out"],
  "Ruby 2.5.0": ["bash /home/cabox/workspace/wcics-grader/ruby.sh"],
  "Ruby 1.9.3p484": ["ruby Main.rb"],
  "Haskell (GHC 7.6.3)": ["ghc -o Main Main.hs", "./Main"],
  "COBOL (OpenCOBOL 1.1.0)": ["cobc -free -x -o Main Main.cbl", "./Main"],
  "Kotlin 1.2.30 (SUPER SLOW)": ["/home/cabox/workspace/wcics-grader/kotlinc/bin/kotlinc Main.kt -include-runtime -d Main.jar", "java -jar Main.jar"]
}

file_exts = {
  "Python 3.6.4": ".py",
  "Python 2.7.6": ".py",
  "Java 9.0.4": ".java",
  "C++ (g++) 4.8.4": ".cpp",
  "C (gcc) 4.8.4": ".c",
  "Ruby 2.5.0": ".rb",
  "Ruby 1.9.3p484": ".rb",
  "Haskell (GHC 7.6.3)": ".hs",
  "COBOL (OpenCOBOL 1.1.0)": ".cbl",
  "Kotlin 1.2.30 (SUPER SLOW)": ".kt"
}

def compress(string,key):
  return string
  if not string:
    return string
  key += chr(0x110000-1)
  chunk = f(len(key))[0]-1
  return "".join(c(string[a:a+chunk]+chr(0x110000-1),key) for a in range(0,len(string),chunk))

def decompress(string,key):
  return string
  if not string:
    return string 
  key += chr(0x110000-1)
  chunk = f(len(key))[1]
  return "".join(d(string[a:a+chunk],key) for a in range(0,len(string),chunk))

def c(string,key):
  try:
    indexes = {key[a]:a for a in range(len(key))}
    num = sum(indexes[string[b]]*len(key)**b for b in range(len(string)))
    power = 1
    string = ""
    while power <= num:
      string += chr((num//power)%256)
      power *= 256
    return string
  except:
    print("Invalid character, not in key!")

def d(string,key):
  num = sum(ord(string[b])*256**b for b in range(len(string)))
  power = 1
  string = ""
  while power <= num:
    string += key[(num//power)%len(key)]
    power *= len(key)
  return string[:-1]
  
def f(n):return min(((ceil(log(256)/log(n)*a),a) for a in range(1,256)),key=lambda a:(ceil(log(256)/log(n)*a[1]) - log(256)/log(n) * a[1],a[1]))

def get_data(name):
  with open("files/problems/%s/tests.json" % name, "r", encoding = "utf-8") as f:
    return json.load(f)

def update_users():
  with open("files/users.json", "w") as f:
    f.write(json.dumps(users))

submissions = json.load(open("files/submissions.json"))

def process_submission(username, password, code, language, problem):
  username = username.strip()
  if users[username]["password"] != password:
    return "/passwordfail"
  if len(username) > 24 or len(username) == 0:
    return "/urbad"
  submission = (username, language, problem, [])
  id = str(int(time() * 1000))
  submissions[id] = submission
  problems = getProblems()
  def proc():
    commands = name_to_command[language]
    foldername = "Submission%s" % id
    try:
      shutil.rmtree(foldername)
    except:
      pass
    os.mkdir(foldername)
    filename = foldername + "/Main" + file_exts[language]
    filename_no_ext = "".join(filename.split(".")[:-1])
    with open(filename, "w+") as f:
      f.write(code)
    for command in commands[:-1]:
      call(shlex.split(command), cwd = foldername)
    def recv(num):
      if num == 5:
        if submission[3][-2] == 5:
          submission[3][-1] += 1
        else:
          submission[3].extend([5, 1])
      else:
        submission[3].append(num)
    test(shlex.split(commands[-1]), get_data(problem), foldername, recv, username, problem, language)
    shutil.rmtree(foldername)
    with open("files/submissions.json", "w") as f:
      f.write(json.dumps(submissions))
  threading.Thread(target = proc).start()
  print("{username} created a submission in {language} for {problem} with id {id}".format(username = username, language = language, problem = problem, id = id))
  print("=" * 50)
  print(code)
  print("=" * 50)
  return "/submission/%s" % id

def get_sorted_users():
  return sorted(list(users), key = lambda u: (sum(users[u]["scores"][p] for p in users[u]["scores"] if p in getProblems()), -users[u]["recency"]), reverse = True)

def getProblems():
  with open("files/contest.txt", "r") as f:
    return f.read().splitlines()

def getFeaturedProblems():
  with open("files/featured.txt") as f:
    return f.read().splitlines()

def fullname(name):
  with open("files/problems/%s/problem.json" % name, "r", encoding = "utf8") as f:
    return json.loads(f.read())["title"]

def getFullNames():
  return list(map(fullname, getProblems()))

def decode(string):
  return base64.b64decode(string.replace("-", "/")).decode("utf-8")

def load_json(bytestring):
  return json.loads("".join(map(chr, bytestring)))

@app.route("/beta")
def serveBeta():
  return redirect("http://wcics-site-alexyjliao153051.codeanyapp.com/")

@app.route("/")
def serveRoot():
  return servePage(0)

@app.route("/page/<int:page>")
def servePage(page):
  global pages
  row = "<tr class='problems'><td><a class='name' href='/problem/%s'>%s</a></td><td class='ctst'>%s</td><td class='tags'>%s</td><td class='pts'>0/%s</td><td class='editorial'><a href=/problem/%s/editorial>Editorial</a></td></tr>"
  featured_row = "<tr class='featured_problems'><td><a class='featured_name' href='/problem/%s'>%s</a></td><td class='featured_ctst'>%s</td><td class='featured_tags'>%s</td><td class='featured_pts'>0/%s</td><td class='featured_editorial'><a href=/problem/%s/editorial>Editorial</a></td></tr>"
  featured_wrapper = "<h1>Featured Problems</h1><table><tr><th>Problem Name</th><th>Category</th><th>Tags</th><th>Points</th><th>Editorial</th></tr>%s</table>"
  with open("files/index.html", "r") as f:
    return f.read() % (featured_wrapper % "".join(featured_row %(problem_map[p]['id'],problem_map[p]['title'],problem_map[p]['ctst'],", ".join(problem_map[p]['tags']),sum(map(int,problem_map[p]['pts'].split("/"))),problem_map[p]['id']) for p in sorted(getFeaturedProblems(),key=lambda x:(sum(map(int,problem_map[x]['pts'].split("/"))),problem_map[x]['id']))) if getFeaturedProblems() else "","".join(row %(problem_map[p]['id'],problem_map[p]['title'],problem_map[p]['ctst'],", ".join(problem_map[p]['tags']),sum(map(int,problem_map[p]['pts'].split("/"))),problem_map[p]['id']) for p in sorted(getProblems(),key=lambda x:(sum(map(int,problem_map[x]['pts'].split("/"))),problem_map[x]['id']))),"".join("<a href='/page/%d'>%d</a>%s"%(a-1,a," "*3 if a != pages else "") for a in range(1,pages+1)),page-1,page+1,str(0 - (page!=0) + (page != pages-1)))
 
@app.route("/tankdoc")
def tankdoc():
  with open("files/tankdoc.html") as f:
    return f.read()

@app.route("/tanksim")
def tanksim():
  with open("files/tanksim.html") as f:
    return f.read()
  
@app.route("/account")
def account():
  return open("files/account.html").read()

@app.route("/stylesheet.css")
def serveStyleSheet():
  with open("files/config.json", "r") as c:
    with open(json.loads(c.read())["maincss"], "r") as f:
      return Response(f.read(), mimetype="text/css")

@app.route("/learnsheet.css")
def serveLearnSheet():
  with open("files/config.json", "r") as c:
    with open(json.loads(c.read())["learncss"], "r") as f:
      return Response(f.read(), mimetype="text/css")

@app.route("/change_style", methods = ["POST"])
def setStyle():
  data = load_json(request.data)
  with open("files/config.json", "r") as f:
    cdat = json.loads(f.read())
  cdat["maincss"] = data["file"]
  with open("files/config.json", "w") as f:
    f.write(json.dumps(cdat))
  return ""

@app.route("/change_learn_style", methods = ["POST"])
def setLearnStyle():
  data = load_json(request.data)
  with open("files/config.json", "r") as f:
    cdat = json.loads(f.read())
  cdat["learncss"] = data["file"]
  with open("files/config.json", "w") as f:
    f.write(json.dumps(cdat))
  return ""

@app.route("/favicon.ico")
def serveIcon():
  with open("files/favicon.ico", "rb") as f:
    return Response(f.read(), mimetype="image/x-icon")

@app.route("/sudo")
def sudo():
  if debug: print("User accessed SUDO page!")
  with open("files/sudo.html", "r") as f:
    return f.read()

@app.route("/urbad")
def urbad():
  return "<link rel='stylesheet' href='/stylesheet.css' type='text/css' /><code><a class='buttonlink' href='/'><<< Back</a>  <a class='buttonlink' href='/enter_submission'>Submit >>></a></code><h1>Username cannot exceed 24 characters or be blank</h1>"

@app.route("/passwordfail")
def passwordfail():
  return "<link rel='stylesheet' href='/stylesheet.css' type='text/css' /><code><a class='buttonlink' href='/'><<< Back</a>  <a class='buttonlink' href='/enter_submission'>Submit >>></a></code><h1>Password was unexpectedly changed between signin and submission, or you are trying to enter submissions through JS fetch without knowing the password field and hoping I didn't check :)</h1>"

@app.route("/js-sha")
def js_sha():
  with open("/home/cabox/workspace/wcics-grader/jsSHA-2.3.1/src/sha.js", "r") as f:
    return f.read()

@app.route("/authjs")
def authjs():
  with open("files/auth.js", "r") as f:
    return f.read()

@app.route("/tankjs")
def tankjs():
  with open("files/tank.js", "r") as f:
    return f.read()

def auth(username, password, **k): # the **k is to allow sudoAuth(**data) instead of sudoAuth(data["username], data["password"])
  return username in users and users[username]["password"] == password

def sudoAuth(username, password, **k):
  return auth(username, password) and username in sudoers

@app.route("/authuser", methods = ["POST"])
def authuser():
  data = load_json(request.data)
  if auth(**data):
    return "auth"
  else:
    return "noauth"

@app.route("/reguser", methods = ["POST"])
def reguser():
  data = load_json(request.data)
  if len(data["username"]) > 24 or len(data["username"]) == 0:
    return "invalid"
  if data["username"] in users:
    return "userexists"
  else:
    users[data["username"]] = {
      "password": data["password"],
      "recency": time(),
      "scores": {}
    }
    update_users()
  return "auth"
@app.route("/clear_leaderboard", methods = ["POST"])
def clear_leaderboard():
  data = load_json(request.data)
  global users
  if sudoAuth(**data):
    users = {}
    update_users()
    print("Leaderboard cleared!")
  else:
    if debug: print("Invalid credentials for clearing leaderboard!")
  return ""

@app.route("/kick_leaderboard", methods = ["POST"])
def kick_leaderboard():
  data = load_json(request.data)
  if sudoAuth(**data):
    __kick_leaderboard(data["name"].strip())
  else:
    if debug: print("Invalid credentials for kicking user!")
  return ""

def __kick_leaderboard(username):
  if username in users:
    del users[username]
    update_users()
    print("Kicked {username} from the leaderboard!".format(username = username))
  else:
    print("Could not kick {username} from the leaderboard because the user does not exist!".format(username = username))

@app.route("/set_user_points", methods = ["POST"])
def set_user_points():
  data = load_json(request.data)
  if sudoAuth(**data):
    __set_points(data["name"], data["prob"], data["pnts"])
  else:
    if debug: print("Invalid credentials for setting user points!")
  return ""

def __set_points(username, problem, points):
  try:
    points = int(points)
    if username not in users:
      users[username] = {"scores": {}, "recency": time()}
    users[username]["recency"] = time()
    users[username]["scores"][problem] = points
    print("Set {username}'s points in {problem} to {points}".format(username = username, problem = problem, points = points))
  except:
    print("The entered data for points is not an integer")

@app.route("/stop_contest", methods = ["POST"])
def stop_contest():
  data = load_json(request.data)
  global running
  if sudoAuth(**data):
    running = False
    with open("files/running.txt", "w") as f:
      f.write("False")
    print("Contest stopped!")
  else:
    if debug: print("Invalid credentials for stopping contest!")
  return ""

@app.route("/start_contest", methods = ["POST"])
def start_contest():
  global running
  data = load_json(request.data)
  if sudoAuth(**data):
    running = True
    with open("files/running.txt", "w") as f:
      f.write("True")
    print("Contest started!")
  else:
    if debug: print("Invalid credentials for starting contest!")
  return ""

@app.route("/add_problem", methods = ["POST"])
def add_problem():
  data = load_json(request.data)
  if sudoAuth(**data):
    __add_problem(data["name"].strip())
  else:
    if debug: print("Invalid credentials for adding problem!")
  return ""

def __add_problem(name):
  if name in os.listdir("files/problems"):
    with open("files/contest.txt", "a", encoding = "utf-8") as f:
      f.write(name + "\n")
    problem_map[name] = json.loads(open("files/problems/%s/problem.json"%name).read())
    print("Added {name} to the contest!".format(name = name))
  else:
    print("Could not add {name} to the contest because the problem does not exist!".format(name = name))

@app.route("/rm_problem", methods = ["POST"])
def rm_problem():
  data = load_json(request.data)
  if sudoAuth(**data):
    __rm_problem(data["name"].strip())
  else:
    if debug: print("Invalid credentials for removing problem!")
  return ""

def __rm_problem(name):
  with open("files/contest.txt", "r", encoding = "utf-8") as f:
    lines = f.read().splitlines()
  index = lines.index(name) if name in lines else -1
  if index != -1:
    print("Removed {name} from the contest!".format(name = name))
  else:
    print("Could not remove {name} from the contest because the problem was not in the contest!".format(name = name))
  with open("files/contest.txt", "w", encoding = "utf-8") as f:
    f.write("\n".join(line for line in lines if line != name) + "\n")

@app.route("/reset_contest", methods = ["POST"])
def reset_contest():
  data = load_json(request.data)
  if sudoAuth(**data):
    __reset_contest()
    print("Contest reset!")
  else:
    if debug: print("Invalid credentials for resetting the contest!")
  return ""

def __reset_contest():
  with open("files/contest.txt", "w", encoding = "utf-8") as f:
    f.write("")

@app.route("/set_contest", methods = ["POST"])
def set_contest():
  data = load_json(request.data)
  if sudoAuth(**data):
    __set_contest(data["contest"])
  else:
    if debug: print("Invalid credentials for setting the contest!")
  return ""

def __set_contest(contest):
  if contest + ".config" in os.listdir("files/contests"):
    with open("files/contests/" + contest + ".config", "r", encoding = "utf-8") as f:
      with open("files/contest.txt", "w", encoding = "utf-8") as g:
        g.write(f.read())
    print("Set the contest to " + contest + "!")
  else:
    print("Could not find contest " + contest + "!")

@app.route("/load_problem", methods = ["POST"])
def load_problem():
  data = load_json(request.data)
  if sudoAuth(data["username"], data["password"]):
    return __load_problem(data["problem"])
  else:
    if debug: print("Invalid credentials for loading a problem!")
  return ""

def __load_problem(problem):
  if problem in os.listdir("files/problems"):
    print("Loaded problem " + problem + "!")
    with open("files/problems/%s/problem.json" % problem, "r") as f:
      return f.read()
  else:
    print("Could not find problem " + problem + "!")
    return ""

@app.route("/load_config", methods = ["POST"])
def load_config():
  data = load_json(request.data)
  if sudoAuth(**data):
    return __load_config(data["contest"])
  else:
    if debug: print("Invalid credentials for loading a contest configuration!")
  return ""

def __load_config(contest):
  if contest + ".config" in os.listdir("files/contests"):
    print("Loaded configuration for contest " + contest + "!")
    with open("files/contests/" + contest + ".config", "r", encoding = "utf-8") as f:
      return f.read().strip()
  else:
    print("Could not find contest " + contest + "!")
    return ""

@app.route("/save_config", methods = ["POST"])
def save_config():
  data = load_json(request.data)
  if sudoAuth(**data):
    __save_config(data["contest"], data["config"])
  else:
    if debug: print("Invalid credentials for setting a contest configuration!")
  return ""

def __save_config(contest, config):
  with open("files/contests/" + contest + ".config", "w", encoding = "utf-8") as f:
    f.write(config.strip() + "\n")
  print("Set configuration for contest " + contest + "!")

@app.route("/del_problem", methods = ["POST"])
def del_problem():
  data = load_json(request.data)
  if sudoAuth(**data):
    __del_problem(data["problem_name"].strip())
  else:
    if debug: print("Invalid credentials for deleting a problem!")
  return ""

def __del_problem(name):
  shutil.rmtree("files/problems/" + name)
  print("Deleted {name} permanently!".format(name = name))
  __rm_problem(name)

@app.route("/write_problem", methods = ["POST"])
def write_problem():
  global problem_map
  data = load_json(request.data)
  if sudoAuth(**data):
    __write_problem(data)
  else:
    if debug: print("Invalid credentials for writing a problem!")
  problem_map = update_probs()
  return ""

def __write_problem(data):
    problem = data
    problem["tags"] = list(map(str.strip, problem["tags"].split(",")))
    print("[-- writing problem {problem_id} --]".format(problem_id = problem["id"]))
    if problem["id"] not in os.listdir("files/problems"):
      print("* creating problem folder...")
      os.mkdir("files/problems/" + problem["id"])
    with open("files/problem_format.html", "r", encoding = "utf-8") as f:
      smpl = problem["smpl"].split("\n")
      smpl = [(smpl[i * 2], smpl[i * 2 + 1]) for i in range(len(smpl) // 2)]
      print("* writing problem JSON file...")
      with open("files/problems/%s/problem.json" % problem["id"], "w") as f:
        f.write(json.dumps(problem))
    print("* done!")
    

@app.route("/create_problem", methods = ["POST"])
def create_problem():
  data = load_json(request.data)
  if sudoAuth(**data):
    __write_problem(data)
    threading.Thread(target = lambda:__create_problem(data)).start()
  else:
    print("Invalid Credentials for creating problem!")
  return ""

def __create_problem(data):
  try:
      problem = data
      print("[-- creating problem {problem_id} --]".format(problem_id = problem["id"]))
      print("=" * 50)
      print(problem["impl"])
      print("=" * 50)
      print(problem["genr"])
      print("=" * 50)
      with open("files/problems/" + problem["id"] + "/" + problem["impl_filename"], "w") as f:
        f.write(problem["impl"])
      with open("files/problems/" + problem["id"] + "/" + problem["genr_filename"], "w") as f:
        f.write(problem["genr"])
      print("* running pre-commands...")
      if problem["impl_precommand"]: check_output(shlex.split(problem["impl_precommand"]), cwd = "files/problems/" + problem["id"] + "/")
      if problem["genr_precommand"]: check_output(shlex.split(problem["genr_precommand"]), cwd = "files/problems/" + problem["id"] + "/")
      pts = list(map(int, problem["pts"].split("/")))
      tls = list(map(int, problem["tls"].split("/"))) * (len(pts) if "/" not in problem["tls"] else 1)
      tcc = list(map(int, problem["tcc"].split("/"))) * (len(pts) if "/" not in problem["tcc"] else 1)
      tests = []
      impl_command, genr_command = shlex.split(problem["impl_command"]), shlex.split(problem["genr_command"])
      for suiteno, (pt, tl, tc) in enumerate(zip(pts, tls, tcc)):
        print("* generating suite {suiteno} of {total}...".format(suiteno = suiteno + 1, total = len(pts)))
        attrs = {}
        tests.append(attrs)
        attrs["timelimit"] = tl
        attrs["points"] = pt
        test_cases = [("", "", "")] * tc
        attrs["tests"] = test_cases
        for case in range(tc):
          c = case
          print("* generating case %d of %d..." % (c + 1, tc))
          test_in = check_output(genr_command, input = bytes(str(suiteno) + "\n" + str(case), "utf-8"), cwd = "files/problems/" + problem["id"] + "/")
          test_out = hashlib.sha384(bytes("".join(map(chr, check_output(impl_command, input = test_in, stderr = sys.stdout, cwd = "files/problems/" + problem["id"] + "/"))).strip(), "utf8")).hexdigest()
          test_in = test_in.decode("utf-8")
          key = "".join(set(test_in))
          test_in = compress(test_in,key)
          test_cases[c] = (test_in, test_out, key)
      print("* writing test case JSON file...")
      with open("files/problems/" + problem["id"] + "/" + "tests.json", "w") as f:
        f.write(json.dumps(tests))
      print("* running post-commands...")
      if problem["impl_postcommand"]: check_output(shlex.split(problem["impl_postcommand"]), cwd = "files/problems/" + problem["id"] + "/")
      if problem["genr_postcommand"]: check_output(shlex.split(problem["genr_postcommand"]), cwd = "files/problems/" + problem["id"] + "/")
      print("* cleaning up generation files...")
      os.remove("files/problems/" + problem["id"] + "/" + problem["impl_filename"])
      os.remove("files/problems/" + problem["id"] + "/" + problem["genr_filename"])
      print("* done!")
  except:
    traceback.print_exc()
    print("Failed on test (First 1024 bytes): " + test_in.decode("utf-8")[:1024])
  update_probs()
  return ""

def getSeries(seriesID):
  for d in lessons():
    if d["seriesID"] == seriesID:return d
    
def getSeriesIndex(seriesID):
  for i,d in enumerate(lessons()):
    if d["seriesID"] == seriesID:return i
  return -1
    
@app.route("/learnsudo")
def learnsudo():
  with open("files/learn/learnsudo.html", "r") as f:
    return f.read()

@app.route("/save_series",methods=["POST"])
def save_series():
  data = load_json(request.data)
  if sudoAuth(**data):
    d = lessons()
    if getSeriesIndex(data["seriesID"])==-1:
      d.append({"seriesID":data["seriesID"]})
    d[getSeriesIndex(data["seriesID"])] = data["data"]
    open("files/learn/lessons.json","w").write(json.dumps(d))
  return ""

@app.route("/load_series",methods=["POST"])
def load_series():
  data = load_json(request.data)
  if sudoAuth(**data):
    if getSeriesIndex(data["seriesID"]) == -1:
      return json.dumps({"seriesID":data["seriesID"],"lessons":[]})
    return json.dumps(getSeries(data["seriesID"]))
  return ""

@app.route("/del_series",methods=["POST"])
def del_series():
  data = load_json(request.data)
  if(sudoAuth(**data)):
    d = lessons()
    if(getSeriesIndex(data["seriesID"])!=-1):
      d.pop(getSeriesIndex(data["seriesID"]))
      open("files/learn/lessons.json","w").write(json.dumps(d))
  return ""
      
@app.route("/del_lesson",methods=["POST"])
def del_lesson():
  data = load_json(request.data)
  if(sudoAuth(**data)):
    d = lessons()
    d[getSeriesIndex(data["seriesID"])]["lessons"].pop(int(data["index"]))
    open("files/learn/lessons.json","w").write(json.dumps(d))
  return ""

@app.route("/move_series",methods=["POST"])
def move_series():
  data = load_json(request.data)
  if sudoAuth(**data):
    d = lessons()
    d.insert(int(data["index"]),d.pop(getSeriesIndex(data["seriesID"])))
    open("files/learn/lessons.json","w").write(json.dumps(d))
  return ""
    
@app.route("/move_lesson",methods=["POST"])
def move_lesson():
  data = load_json(request.data)
  if sudoAuth(**data):
    d = lessons()
    print(d[getSeriesIndex(data["seriesID"])],data)
    toIns = d[getSeriesIndex(data["seriesID"])]["lessons"].pop(int(data["pop_index"]))
    d[getSeriesIndex(data["seriesID"])]["lessons"].insert(int(data["index"])+1,toIns)
    open("files/learn/lessons.json","w").write(json.dumps(d))
  return ""

def blink(text, url, disabled = False,classes=""):
  return "<button class='buttonlink %s'%s onclick='window.open(\"%s\", \"_self\")'>%s</button>" % (classes," disabled" if disabled else "", url, text)

def createHeader(data, lesson):
  lessons = data["lessons"]
  for index,l in enumerate(lessons):
    if l["lessonID"] == lesson:
      break
  else:
    index = -1
  ids = list(map((lambda x:x["lessonID"]),lessons))
  id = data["seriesID"]
  return "<a class='buttonlink' href='/learn'><<< Back</a>  " + "  ".join(blink(x, y,z) for x, y, z in [
    ("<<< Intro", "/learn/%s" % (id), index == 0),
    ("<< First" if index else "First >>", "/learn/%s/%s" % (id, ids[1] if len(ids)>1 else ""), index == 1 or len(ids)==1),
    ("< Prev", "/learn/%s/%s" % (id, ids[(index - 1) % len(ids)]), index <= 1),
    ("Next >", "/learn/%s/%s" % (id, ids[(index + 1) % len(ids)]), index + 1 == len(ids)),
    ("Last >>", "/learn/%s/%s" % (id, ids[-1]), index + 1 == len(ids)),
  ]) + "<br /><br />"

@app.route("/learn")
def learnPage():
  return open("files/learn/template.html").read()%("Learn!","<center><h1>Series</h1>"+"<br />".join(blink(a["lessons"][0]["title"],"/learn/"+a["seriesID"],False,"centerButton") for a in lessons()) + "</center>")


@app.route("/learn/<series>")
def seriesPage(series):
  return open("files/learn/template.html").read()%("Introduction to %s"%getSeries(series)["lessons"][0]["title"],createHeader(getSeries(series),"intro")+getSeries(series)["lessons"][0]["bodyHTML"]+"<center>" + "<br /><h2>Lessons</h2><hr /><br />"+"<br />".join(blink(a["title"],"/learn/%s/%s"%(series,a["lessonID"]),False,"centerButton") for a in getSeries(series)["lessons"][1:]) + "</center>")

@app.route("/learn/<series>/<lesson>")
def lessonPage(series,lesson):
  data = getSeries(series)
  lssns = data["lessons"]
  for index,l in enumerate(lssns):
    if l["lessonID"] == lesson:
      break
  else:
    index = -1
  return open("files/learn/template.html").read()%(lssns[index]["title"],createHeader(data,lesson) + lssns[index]["bodyHTML"])

@app.route("/problem/<id>")
def problem(id):
  with open("files/problems/%s/problem.json" % id, "r") as p:
    with open("files/problem_format.html", "r") as f:
      p = json.loads(p.read())
      title = p["title"]
      desc = p["desc"]
      subt = p["subt"]
      inpt = p["inpt"]
      outp = p["outp"]
      smpl = p["smpl"].split("\n")
      return f.read() % (title, p['id'],p['id'], title, desc.replace("\n", "<br />"), inpt.replace("\n", "<br />"), outp.replace("\n", "<br />"), subt.replace("\n", "<br />"), "\n".join("<h3>Sample Input</h3>\n<table class='sample'><tr><td><code>%s</code></td></tr></table>\n<h3>Sample Output</h3>\n<table class='sample'><tr><td><code>%s</code></td></tr></table>" % (smpl[2 * r], smpl[2 * r + 1]) for r in range(len(smpl) // 2)))

@app.route("/problem/<id>/editorial")
def editorial(id):
  if id not in problem_map:
    return open("files/inv_prob.html").read() % id
  p = problem_map[id]
  if "edit" not in p:
    return open("files/inv_editorial.html").read() % (id,p["title"])
  return open("files/editorial.html").read() % (p["title"],id,p["title"],p["edit"].replace("\n","<br />"))

#@app.route("/leaderboard")
def leaderboard():
  problems = getProblems()
  config = [(user, [users[user]["scores"].get(problem, 0) for problem in problems]) for user in get_sorted_users()]
  return open("files/leaderboard.html", "r").read() % "".join(
    "<tr><td>%s</td><td>%d</td><td hidden class='rcol leaderboard'>%s</td></tr>" % (html.escape(user), sum(cfg), " / ".join(map(str, cfg))) for user, cfg in config)

@app.route("/enter_submission/<id>")
def enter_submission(id):
  return submission_file(id, False)

@app.route("/tank_game")
def tank_game():
  with open("files/tank_game.html") as f:
    return f.read()
  
def submission_file(id, sudomode = False):
  if id not in problem_map:
    id = "hello-world"
  with open("files/template.html", "r") as f:
    return f.read() % (
      "".join(
        "<option value='{language}'>{language}</option>".format(language = language)
      for language in name_to_command.keys()),
      "".join(
        "<option value='{id}'>{problem}</option>".format(id = p, problem = getFullNames()[i])
      for i, p in enumerate(getProblems())),id,
    "submit_sudo" if sudomode else "submit")

@app.route("/running")
def is_running():
  return str(running)
  
@app.route("/admin_auth", methods=["POST"])
def admin_auth():
  data = load_json(request.data)
  return "auth" if sudoAuth(**data) and data["username"] in sudoers else ""

@app.route("/submit", methods = ["POST"])
def submit():
  return process_submission(**load_json(request.data))

@app.route("/submit_sudo")
def submit_sudo(userhash, data):
  return process_submission(**json.loads(decode(data)))

@app.route("/submission/<id>")
def submission(id):
  if id not in submissions:
    return "<title>Submission not found</title><link rel='stylesheet' href='/stylesheet.css' type='text/css' /><p style='font-family:monospace'>Sorry, submission not found with that ID.</p>"
  return "<title>Submission</title><link rel='stylesheet' href='/stylesheet.css' type='text/css' /><a class='buttonlink' href='/problem/%s'><<< Back</a><br /><br /><a class='buttonlink' href='/enter_submission/%s'>Resubmit</a><br /><br />Submitted by '%s' in %s for %s<br /><br />" % tuple(submissions[id][q] for q in [2, 2, 0, 1, 2]) + "<br />".join(stringify(submissions[id][3]))

# 0, b => Test Suite # [$b point(s)]
# 1, b => Test # passed: $b seconds
# 2, b => Test # failed: Wrong Answer: $b seconds
# 3, b => Test # failed: Time Limit Exceeded: $b seconds
# 4, b => Test # failed: Runtime Error: $b seconds
# 5, b => Test #..b..# skipped

def stringify(data):
  data = data[::-1]
  suite = 0
  tcase = 0
  while data:
    id = data.pop()
    if id == 0:
      suite += 1
      tcase = 0
      yield "<p class='suite subinfo'>Test Suite %d [%d point%s]</p>" % (suite, data[-1], "" if data.pop() == 1 else "s")
    elif id == 1:
      tcase += 1
      yield "<p class='AC subinfo'>Test %d passed: %s seconds</p>" % (tcase, data.pop())
    elif id == 2:
      tcase += 1
      yield "<p class='WA subinfo'>Test %d failed: Wrong Answer: %s seconds</p>" % (tcase, data.pop())
    elif id == 3:
      tcase += 1
      yield "<p class='TLE subinfo'>Test %d failed: Time Limit Exceeded: %s seconds</p>" % (tcase, data.pop())
    elif id == 4:
      tcase += 1
      yield "<p class='RTE subinfo'>Test %d failed: Runtime Error: %s seconds</p>" % (tcase, data.pop())
    elif id == 5:
      for _ in range(data.pop()):
        tcase += 1
        yield "<p class='SKIP subinfo'>Test %d skipped</p>" % tcase
    elif id == 6:
      yield "<p class='result subinfo'>Total Points: %d / %d</p>" % (data.pop(), data.pop())

@app.route("/run_command",methods = ["POST"])
def run_command():
  data = load_json(request.data)
  if sudoAuth(data["username"],data["password"]): 
    command = data["command"]
    print("Processing manual command `{command}`".format(command = command))
    process_command(shlex.split(command))
  else:
    if debug:print("Invalid Credentials for running command!")
  return ""

@app.route("/scores/<username>")
def scores(username):
  if username not in users:return ""
  return json.dumps(users[username]["scores"])
@app.route("/todo")
def todo():
  with open("files/todo.html") as f:
    return f.read() % open("files/todo.txt").read()

@app.route("/todo/write", methods = ["POST"])
def todo_write():
  data = load_json(request.data)
  with open("files/todo.txt","w+") as f:
    f.write(data['text'])
  return ""

@app.route("/maintenance")
def maintenance():
  return open("files/maintenance.html").read()

@app.route("/change_user", methods = ["POST"])
def change_user():
  new = load_json(request.data)["new"]
  old = load_json(request.data)["old"][18:-18]
  if not old or not new and old not in users or new in users:return ""
  stored = users[old]
  users[new] = stored
  del users[old]
  update_users()
  return "success"

@app.route("/change_pass", methods = ["POST"])
def change_pass():
  data = load_json(request.data)
  if data["username"]:
    users[data["username"]]["password"] = data["password"]
  update_users()
  return "success"

def process_command(command):
  if command == []:
    return
  if command[0] == "remove":
    __rm_problem(command[1])
  elif command[0] == "add":
    __add_problem(command[1])
  elif command[0] == "stop" or command[0] == "pause":
    stop_contest()
  elif command[0] == "start" or command[0] == "resume":
    start_contest()
  elif command[0] == "kick":
    __kick_leaderboard(command[1])
  elif command[0] == "clearboard":
    clear_leaderboard(serverhash)
  elif command[0] == "setpoints":
    __set_points(command[1], list(map(int, command[2].split("/"))))
  elif command[0] == "clear":
    sys.stdout.write("\033[2J\033[1;1H")
  elif command[0] == "eval":
    try:
      print(eval(command[1]))
    except:
      traceback.print_exc()
  elif command[0] == "shutdown":
    print("Server shutting down!")
    shutdown = request.environ.get("werkzeug.server.shutdown")
    if shutdown is not None:
      shutdown()
  else:
    threading.Thread(target = lambda: [call(command)] and os.chdir("/home/cabox/workspace/wcics-grader")).start()

if __name__ == "__main__":
  if len(sys.argv) >= 2:
    try:
      port = int(sys.argv[1])
    except:
      port = 80
  else:
    port = 80
  print("* starting!")
  app.run(host = "0.0.0.0", port = port, debug = "--debug" in sys.argv)