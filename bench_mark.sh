sudo apt-get install -y libaio1 libmariadb3 libpq5 mariadb-common mysql-common sysbench
sysbench --test=cpu --cpu-max-prime=10000 --num-threads=4 run