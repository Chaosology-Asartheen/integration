import numpy as np;
import cv2;
import imutils;

roiPts = []

def main():
    global FRAME, roiPts, mode, paused;
    width = 1200;
    height = 600;
    termination = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 1);
    key = None;
    currentFrame = None;
    modeTracker = [0];

    # set the frame to all white
    camera = cv2.VideoCapture(0);
    _, FRAME = camera.read()
    # FRAME = np.zeros((height, width, 3), np.uint8); 
    # FRAME[:, :] = (255, 255, 255);

    # Window is the window we are showing 
    cv2.namedWindow("Window");
    cv2.setMouseCallback("Window", mouse_click);

    ##########################################################################

    orig = FRAME.copy();
            
    # We are going only going to click the 1, 2, 3 balls
    while len(roiPts) < 4:
        cv2.imshow("Window", FRAME);
        cv2.waitKey(0);

    while True:
        print("Trying to do some cv magic")
        # determine the top-left and bottom-right points
        roiPts = np.array(roiPts)
        s = roiPts.sum(axis = 1)
        tl = roiPts[np.argmin(s)] # top left pixel
        br = roiPts[np.argmax(s)] # bottom right pixel

        # grab the ROI for the bounding box and convert it
        # to the HSV color space
        roi = orig[tl[1]:br[1], tl[0]:br[0]]
        roi = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
        #roi = cv2.cvtColor(roi, cv2.COLOR_BGR2LAB)

        # compute a HSV histogram for the ROI and store the
        # bounding box
        roiHist = cv2.calcHist([roi], [0], None, [16], [0, 180])
        
        roiHist = cv2.normalize(roiHist, roiHist, 0, 255, cv2.NORM_MINMAX)

        frame = imutils.resize(frame, width = 600);
        frame = cv2.flip(frame, 1); # flip across y axis
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # calculate and display backprojection again
        backProj = cv2.calcBackProject([hsv], [0], roiHist, [0, 180], 1)
            
        newBackProj = np.zeros((337, 600, 3), np.uint8);
        newBackProj[:,:,0] = backProj[:,:];
        newBackProj[:,:,1] = newBackProj[:,:,2] = newBackProj[:,:,0];

        FRAME[0 + 120:337 + 120,:600] = newBackProj[:,:];

        # apply cam shift to the back projection, convert the
        # points to a bounding box, and then draw them
        try: # if the selected points are not working, we catch that
            (r, roiBox) = cv2.CamShift(backProj, roiBox, termination)
            pts = np.int0(cv2.cv.BoxPoints(r))
            for pt in pts:
                pt[1] = pt[1] + 120;
                
            cv2.polylines(FRAME, [pts], True, (0, 255, 0), 2)
        except:
            print("Lmao ur fcked")
            return None
        
        FRAME[0 + 120: 337 + 120, :600] = frame[:, :]

        ##########################################################################

        cv2.imshow("Window", FRAME); # update the window with the new graphics

    # we need these two functions otherwise we will not release resources
    camera.release();
    cv2.destroyAllWindows();

def mouse_click(event, x, y, flags, param):
    global FRAME, roiPts

    if event == cv2.EVENT_LBUTTONDOWN:
        roiPts.append((x, y))
        cv2.circle(FRAME, (x, y), 4, (0, 255, 0), 2)
        cv2.imshow("Window", FRAME)
        print("click", (x, y))

if __name__ == "__main__":
    main()