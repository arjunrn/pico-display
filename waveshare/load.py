import urequests
import network

ssid = "TP-LINK_DE78_24"
password = "71861838"

if __name__ == "__main__":
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)

    # Wait for connect or fail
    max_wait = 10
    while max_wait > 0:
        if wlan.status() < 0 or wlan.status() >= 3:
            break
        max_wait -= 1
        print("waiting for connection...")
        time.sleep(1)

    # Handle connection error
    if wlan.status() != 3:
        raise RuntimeError("network connection failed")
    else:
        print("connected")
        status = wlan.ifconfig()
        print("ip = " + status[0])
    response = urequests.get("http://192.168.1.13:30080/images/dashboard.epdimg")
    print(len(response.content))
    response.close()
    print("finished")
