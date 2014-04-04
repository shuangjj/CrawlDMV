#!/usr/bin/env python
import urllib

def main():
    dmv_url = "http://www.dmv.state.pa.us/"
    reg_url = "https://www.dot3.state.pa.us/exam_scheduling/eslogin.jsp"    #TODO Hardcode here
    # Top dmv page
    htmltop = urllib.urlopen(reg_url).read();
    print htmltop
    

if __name__ == "__main__":
    main()
