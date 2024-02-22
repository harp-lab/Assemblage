# Assemblage

## AWS Deployment Instructions 

Assemblage is mainly tested on AWS. If you plan to use AWS services, please copy your confidential file to `$ASSEMBLAGE_HOME/aws` before system initialization, which should contains the private key and geo information

### Builder/Crawler APIs

#### Crawler Data Source

A crawler is provided with the system, it need a object of data source, which is the website it crawls,the constructor for such data source is provided as `GithubRepositories`, which takes in tokens, query parameters and query time intervals, for example:

```
GithubRepositories(
    git_token="",
    qualifier={
        "language:c",
        "stars:>2"
    }, 
    crawl_time_start= start,
    crawl_time_interval=querylap,
    crawl_time_lap=querylap,
    proxies=[],
    build_sys_callback=get_build_system
    # sort="stars", order="desc"
)

```

It is also possible to implement crawler to other websites by extending the `DataSource` class

#### Worker APIs: 

Worker API extends `BuildStartegy` class, and provides a comprehensive coverage of behavior of 3 stages: cloning, building, build_callback.

* Clone: `get_clone_dir` specify the clone data's destination path, `clone_data` should clone the source code to the provided destination path.
* Compile/Build: `run_build` specifies the behavior during building, such as how to call cmd/modify the files.
* Binary Collection: `post_build_hook` is used to deal with files after the build process exited.

#### Example Workers

an example of worker can be found at [example_cluster.py](../example_cluster.py), [example_windows.py](../example_windows.py), [example_vcpkg.py](../example_vcpkg.py).

If you don't need customization, check [stable branches](https://github.com/harp-lab/Assemblage/branches) that has been deployed and tested.


### Deployment


1. Create the docker network
```
docker network create assemblage-net
```

2. Build docker images
```
./build.sh
```

2. Run and initialize MySQL.
```
docker pull mysql/mysql-server
# publish port 3306 and add a volume so the data can be accessed locally.
docker run --name=mysql -v $(pwd)/db-data:/var/lib/mysql -p 3306:3306 --network=assemblage-net -d mysql/mysql-server
docker logs mysql
# find the tmp password in log
# may need to wait a minute for the database to initialize
# and the password is provided
docker exec -it mysql mysql -uroot -p


# set password to 'assemblage', change this for your own
# Make sure to set the DB password in the coordinators config
# before building the image.
mysql> ALTER USER 'root'@'localhost' IDENTIFIED BY 'assemblage';
mysql> CREATE USER 'root'@'%' IDENTIFIED BY 'assemblage';
mysql> GRANT ALL PRIVILEGES ON *.* TO 'root'@'%' WITH GRANT OPTION;
mysql> CREATE DATABASE IF NOT EXISTS assemblage;
```

3. Initialize the Database
```
# Run cli.py and follow the intructions, it will create tables and setup other configs
pip3 install -r requirements.txt
python3 cli.py
```


4. Use `start.sh` or `stop.sh` to start up the services if needed
```
sh start.sh
sh stop.sh
```

5. Boot CLI

As Google changed some of the codes, you need to add the flag `PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python` to boot CLI tools

```
pip3 install pyfiglet prompt_toolkit pyfiglet plotext pypager grpcio grpcio-tools
PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python python3 cli.py --server $(docker inspect --format '{{ $network := index .NetworkSettings.Networks "assemblage-net" }}{{ $network.IPAddress}}'  assemblage_coordinator_1):50052
```
