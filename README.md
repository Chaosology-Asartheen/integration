In order for BreakTime to run smoothly, the following parameters may require tuning:

Open Logitech software
  Turn off focus, set focus all the way to the left
  White balance (around 75%)

main
  main
    Frame cropping points

cv
  cue_stick_detection
    Cue stick tip seems off? --> MIN_TIP_AREA, MAX_TIP_AREA
    Cue stick midpoint seems off? --> MIN_CUESTICK_AREA, MAX_CUESTICK_AREA
  hough_circles
    Green dots are flashing everywhere? --> Fix ignore regions in cv/constants.py
