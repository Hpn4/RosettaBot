import requests
import json
import time
import cloudscraper
import base64
import xml.etree.ElementTree as ET

import argparse

def get_grapq_payload(course):
    s = r"""{
    "operationName":"GetCourseMenu",
    "variables":{
        "languageCode":"%s",
        "filter":"ALL",
        "chunking":false,
        "includeMilestoneInLessonFour":true
        },
    "query":"query GetCourseMenu($languageCode: String!, $filter: String!, $includeMilestoneInLessonFour: Boolean!, $chunking: Boolean!) {\n  courseMenu(\n    languageCode: $languageCode\n    includeMilestoneInLessonFour: $includeMilestoneInLessonFour\n    chunking: $chunking\n    filter: $filter\n  ) {\n    currentCourseId\n    bookmarkToUseOnload {\n      course\n      bookmarkToUseOnload\n      __typename\n    }\n    speechEnabledBookmark {\n      course\n      unitIndex\n      lessonIndex\n      pathType\n      __typename\n    }\n    speechDisabledBookmark {\n      course\n      unitIndex\n      lessonIndex\n      pathType\n      __typename\n    }\n    curriculumDefaults {\n      course\n      curriculumId\n      resource\n      __typename\n    }\n    viperDefinedCurricula {\n      id\n      course\n      firstExerciseId\n      exerciseCount\n      nameByLocale {\n        curriculumId\n        locale\n        curriculumNameLocalized\n        __typename\n      }\n      descriptionByLocale {\n        curriculumId\n        locale\n        curriculumDescriptionLocalized\n        __typename\n      }\n      __typename\n    }\n    showCurriculumChooser {\n      course\n      showCurriculumChooser\n      __typename\n    }\n    numberOfUnits\n    units {\n      id\n      index\n      unitNumber\n      titleKey\n      color\n      colorDesaturated\n      lessons {\n        id\n        index\n        titleKey\n        lessonNumber\n        paths {\n          unitIndex\n          lessonIndex\n          curriculumLessonIndex\n          sectionIndex\n          index\n          type\n          id\n          course\n          resource\n          scoreThreshold\n          timeEstimate\n          numChallenges\n          numberOfChallengesSeen\n          complete\n          scoreCorrect\n          scoreIncorrect\n          scoreSkipped\n          percentCorrectForDisplay\n          percentIncorrect\n          percentSkipped\n          percentComplete\n          pathCourseMenuDisplayState\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n  tutoringSummary {\n    status\n    canSchedule\n    userTimezone\n    nextSession {\n      startTimeStamp\n      lessonNumber\n      unitNumber\n      coachName\n      __typename\n    }\n    __typename\n  }\n}\n"}
    """ % (course)

    return s

def build_course_payload(course_code, unit, lesson, ptype, occ, ch, time):
    s = """<path_score>
    <course>%s</course>
    <unit_index>%d</unit_index>
    <lesson_index>%d</lesson_index>
    <path_type>%s</path_type>
    <occurrence>%d</occurrence>
    <complete>true</complete>
    <score_correct>%d</score_correct>
    <score_incorrect>0</score_incorrect>
    <score_skipped type="fmcp">0</score_skipped>
    <number_of_challenges>%d</number_of_challenges>
    <delta_time>%s</delta_time>
    <version>130422</version>
    <updated_at>1701427600088</updated_at>
    <is_lagged_review_path>false</is_lagged_review_path>
    </path_score>""" % (course_code, unit, lesson, ptype, occ, ch, ch, time)

    return s

def build_course_step_payload(course_code, unit, less, ptype, step_id, ch):
    s = """<path_step_score>
     <course>%s</course>
     <unit_index>%d</unit_index>
     <lesson_index>%d</lesson_index>
     <path_type>%s</path_type>
     <occurrence>1</occurrence>
     <path_step_media_id>%s</path_step_media_id>
     <complete>true</complete>
     <score_correct>%d</score_correct>
     <score_incorrect>0</score_incorrect>
     <score_skipped type="fmcp">0</score_skipped>
     <number_of_challenges>%d</number_of_challenges>
     <speech_was_enabled>true</speech_was_enabled>
     <version>130422</version>
     <updated_at>1701427949810</updated_at>
     </path_step_score>""" % (course_code, unit, less, ptype, step_id, ch, ch)

    return s

s = cloudscraper.create_scraper()

#api.get_home()
def get_field(cont, field):
    return cont.split(field)[1].split("\"")[0]

# Get headers and payload from request formatted as Curl
def construct_from_fetch(file):
    f = open(file, "rb")
    cont = f.read()
    cont = cont.decode("utf-8")
    f.close()

    # Get headers
    headers = {}
    for h in cont.split("-H"):
        h = h.split("'")[1]
        if h.startswith("https"):
            continue

        k,v = h.split(": ")
        headers[k] = v

    # Get body
    rbody = cont.split("--data-raw '")[1].split("'")[0]
    body = json.loads(rbody)

    return (headers, rbody, body)

# Send start session and parse it
# Parse response of the session start to get url, token, userid, courseid
def parse_resp(headers, body):
    s.headers = headers

    r = s.post("https://lcp.rosettastone.com/api/v3/session/start", json=body)

    resp = r.text
    imp = resp.split("tracking_service")[1]

    token = get_field(imp, "web_service_access_key\":\"")
    user_id = get_field(imp, "user_id\":\"")
    url = get_field(imp, "web_service_base_url\":\"")

    course = get_field(resp, "last_run_course\":\"")
    course_id = get_field(resp, "product_identifier\":\"")

    url += f"users/{user_id}"

    print("User id:", user_id)
    print("Auth token:", token)
    print("Profiling URL:", url)
    print("Course code:", course)
    print("Course id:", course_id)

    return course_id, url, token

# Return all units in json format
def get_graphq(headers, rbody, course_id):
    # Build authorization token
    auth = "{\"viperMode\":true,\"k12\":false,\"sqrlAuth\":"
    auth += rbody
    auth += ",\"welcomePacket\":{}}"

    auth = base64.b64encode(auth.encode('utf-8'))
    auth = auth.decode('utf-8')

    # Generate X-Request-ID
    x_req_id = "5478133f-cf92-46cb-b742-283686e1028a"

    payload = get_grapq_payload(course_id)
    payload = json.loads(payload)

    s.headers = {
        "Authorization": auth,
        "X-Request-Id": x_req_id,
        "User-Agent": headers["user-agent"]
    }

    resp = s.post("https://graph.rosettastone.com/graphql", json=payload)
    units = resp.json()['data']['courseMenu']['units']

    return units

# Return all the exercices of the lessons
def get_lessons_ex(base_url, path, token):
    course_code = path['course']
    unit_ind = path['unitIndex']
    les_ind = path['lessonIndex']
    path_t = path['type']
    occ = 1

    url = base_url
    url += f"/path_step_scores?course={course_code}"
    url += f"&unit_index={unit_ind}&lesson_index={les_ind}"
    url += f"&path_type={path_t}&occurrence={occ}&method=get"

    url_put = base_url
    url_put += f"/path_step_scores?course={course_code}"
    url_put += f"&unit_index={unit_ind}&lesson_index={les_ind}"
    url_put += f"&path_type={path_t}&occurrence={occ}"

    print("Grant subexo:", url)

    s.headers = {
        "X-Rosettastone-Session-Token": token,
        "X-Rosettastone-Protocol-Version": "8",
        "Content-Type": "text/xml"
    }

    resp = s.get(url)

    root = ET.fromstring(resp.text)

    for ch in root:
        cha = int(ch[4].text)
        step_id = ch[6].text
        pay = build_course_step_payload(course_code, unit_ind, les_ind, path_t, step_id, cha)

        med_url = url_put + f"&path_step_media_id={step_id}&_method=put"
        
        print(med_url)
        resp = s.post(med_url, data=pay)

        print(resp.status_code)

def grant_hour(base_url, path, token, hour):
    m = int(round(hour * 60) // 8)

    course_code = path['course']
    unit_ind = path['unitIndex']
    les_ind = path['lessonIndex']
    path_t = path['type']
    occ = 1

    ch = path['numChallenges']
    t = "90000000000000000000000"

    url = base_url
    url += f"/path_scores?course={course_code}"
    url += f"&unit_index={unit_ind}&lesson_index={les_ind}"
    url += f"&path_type={path_t}&occurrence={occ}&_method=put"

    s.headers = {
        "X-Rosettastone-Session-Token": token,
        "X-Rosettastone-Protocol-Version": "8",
        "Content-Type": "text/xml"
    }

    js = build_course_payload(course_code, unit_ind, les_ind, path_t, occ, ch, t)

    print(js)

    for i in range(m):
        resp = s.post(url, data=js)

    print(resp.text)
    print(resp.status_code)

parser = argparse.ArgumentParser(description='Rosetta bot.')

parser.add_argument('-u', '--unit', default=0, type=int, help='Unit index')
parser.add_argument('-l', '--lesson', default=0, type=int, help='Lesson index')
parser.add_argument('-e', '--exercice', default=0, type=int, help='Exercice index')
parser.add_argument('-t', '--hour', default=0, type=float, help='Number of hours in float')
parser.add_argument('-v', '--validate', default=False, type=bool, help='Validate or not the erxercice')
parser.add_argument('-f', '--file', default="", type=str, required=True, help='File where cookies are stored. copy as curl bash from start')

args = parser.parse_args()

print(f"--- Read data from {args.file} ---")
headers, rbody, body = construct_from_fetch(args.file)
course_id, base_url, token = parse_resp(headers, body)
units = get_graphq(headers, rbody, course_id)

exo = units[args.unit]['lessons'][args.lesson]['paths'][args.exercice]

print(f"--- Operate on n°{args.exercice} in lesson {args.lesson} of unit {args.unit} ---")

if args.validate:
    print("--- Grant exercice ---")
    get_lessons_ex(base_url, exo, token)
else:
    print(f"--- Grant {args.hour} hours ---")

    grant_hour(base_url, exo, token, args.hour)