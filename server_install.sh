#step 1
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt-get update

#2
sudo apt-get install python3.12

#3
python3 -m venv venv
source venv/bin/activate

#4
pip install -r requirements.txt

#5
