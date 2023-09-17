# coding=utf-8 
import sys 
import json 
import requests 
from fake_useragent import UserAgent
import random 


def solve(nickname):
    # 模拟客户端发送信息 
    try:
        imfo_t = "user.info" 
        ex_url = f"https://codeforces.com/api/{imfo_t}"

        ex_user_agent = UserAgent()
        ex_header = {"User-Agent": ex_user_agent.random} 
        # print(ex_user_agent.random)

        ex_par = {"handles": nickname} 
        response = requests.get(ex_url, params=ex_par , headers=ex_header)
        
        # 分析结果 
        if response.status_code != 200 :
            print("no such handle") 
        else : 
            data = json.loads(response.text) 
            if data["status"] == "FAILED": 
                print("no such handle") 
                sys.exit(1) 
            elif data["result"][0]["contribution"] == 0 :
                people = {
                    "handle" : nickname[0] 
                }
                print(json.dumps(people) , file= sys.stdout) 
                sys.exit(0)
            elif data["result"][0]["contribution"] != 0 :
                people = {
                    "handle" : nickname[0] , 
                    "rating" : data["result"][0]["rating"],
                    "rank" : data["result"][0]["rank"] 
                }
                print(json.dumps(people) , file= sys.stdout) 
                sys.exit(0)
    except IndexError:
        print("no such handle", file=sys.stderr)
        sys.exit(1)
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"An error occurred while parsing JSON: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)
    return 0 

def main():
    print("please input a nickname :")
    nickname = sys.stdin.readline().split() 
    solve(nickname) 

if __name__ == "__main__" :
    main() 