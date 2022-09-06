# Assm analyze class

## Analyze class
*   **init**  
    Input: string:address of mysql  
    Output: object: Analyze  
    Usage: constructor of Analyze object

*   **stop**  
    Input: None  
    Output: None  
    Usage: Stop the connection to DB, this object can be discarded  

*   **removedup_status**  
    Input: List[Status]  
    Output: List[Status]  
    Usage: Remove the duplicates in List by Status->id  
    Warn: Not well designed with O(n^2), don't use in large list

*   **peek**  
    Input: None,int  
    Output: None  
    Usage: Print useful info about the db  


*   **dumperr_csv**  
    Input: None,int  
    Output: None  
    Usage: Dump all unique non-empty build message into errs.csv
    Warn: No longer maintended

*   **dumprepo_csv**  
    Input: None(recommended),int  
    Output: None  
    Usage: Dump the repos in db into repos.csv  

*   **analyze_err**  
    Input: int(max item to display, recommend 10)  
    Output: None  
    Usage: Visualize error message   
    Warn: No longer maintended  

*   **analyze_reposworker**  
    Input: List[int],List[String],String,String,Int  
    Output: None   
    Usage: A one-threaded worker  
    Warn: Don't call it unless necessary

*   **fetch_repos**  
    Input: None  
    Output: None  
    Usage: Load token.json, then compare the repos.csv and repos_files.csv for unfinished work, assigned equally to workers with tokens stored in token.json  
    Warn: Load unfinished work runs O(n^2) on one thread, but iteration speed will increase linearly with time running (lowest 100 on our server) takes around 1-2 hours.

*   **analyze_buildsys**  
    Input: List[String]  
    Output: String  
    Usage: Given list of file name, return the guess of the build tool in these files.  
    Warn: The result lies in one of this dict key, matching keyword lies in the dict val  
    ```
    {"make":["makefile"],  
    "cmake":["cmakelists.txt"],   
    "travisci":[".travis.yml"],   
    "circleci":["config.yml"],   
    "rake":["rakefile"],   
    "sln":[".sln"],   
    "autoconf":["configure"],  
    "java":["build.gradle","gradlew","pom.xml"],  
    "ninja":["ninja","build.ninja"]}  
    ```

*   **analyze_files**  
    Input: None  
    Output: None  
    Usage: Print the table of analysis of the build tool stored in repos_files.csv  


## TokenChecker class

*   **init**  
    Input: None     
    Output: object: TokenChecker    
    Usage: constructor of TokenChecker    

*   **checkall**  
    Input: None  
    Output: None  
    Usage: Print the core rate limit for all tokens stored in token.json

*   **ratelimit**
    Input: String(username), String(token)  
    Output: Dict  
    Usage: return the raw parsed json as dict  

*   **core_remaining**  
    Input: String(username), String(token)  
    Output: Int  
    Usage: return the remaining of **core** API call  

*   **core_reset**  
    Input: String(username), String(token)  
    Output: Int  
    Usage: return the remaining time for next **core** API call resetting from now as int
    Warn: The wait time is added by 3 for code for code safety

*   **search_remaining**  
    Input: String(username), String(token)  
    Output: Int  
    Usage: return the remaining of **search** API call  

*   **core_reset**  
    Input: String(username), String(token)  
    Output: Int  
    Usage: return the remaining time for next **search** API call resetting from now as int
    Warn: The wait time is added by 3 for code for code safety

*   **code_remaining**  
    Input: String(username), String(token)  
    Output: Int  
    Usage: return the remaining of **code_scanning_upload** API call  

*   **code_reset**  
    Input: String(username), String(token)  
    Output: Int  
    Usage: return the remaining time for next **code_scanning_upload** API call resetting from now as int
    Warn: The wait time is added by 3 for code for code safety

## Data->update_build->UpdateMakeSys

*   **init**  
    Input: None     
    Output: object: UpdateMakeSys    
    Usage: constructor of UpdateMakeSys

*   **write2db**  
    Input: string:address of mysql  
    Output: None  
    Usage: Write the analysis result into db, refer to Analyze->analyze_buildsys
