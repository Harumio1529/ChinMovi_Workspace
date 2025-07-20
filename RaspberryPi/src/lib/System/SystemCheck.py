import subprocess

def is_wifi_connected():
    try:
        result = subprocess.check_output(["iwgetid", "-r"]).decode().strip()
        return result != ""
    except subprocess.CalledProcessError:
        return False

def wifi_off():
    if is_wifi_connected()==True:
        subprocess.run(["rfkill", "block", "wifi"], check=True)

def wifi_on():
    if is_wifi_connected()==False:
        subprocess.run(["rfkill", "unblock", "wifi"], check=True)


def switch_network():
    if is_wifi_connected():
        wifi_off()
    else:
        wifi_on()


if __name__=="__main__":
    if is_wifi_connected():
        wifi_off()
        print("wifioff")
    else:
        wifi_on()
        print("wifion")