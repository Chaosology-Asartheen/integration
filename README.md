In order for BreakTime to run smoothly, the following parameters may require tuning:

Open Logitech software
  Turn off focus, set focus all the way to the left
  White balance (around 75%)

main
  main
    Frame cropping points
    use ID card to measure true frame points and modify X_CM_OFFSET and Y_CM_OFFSET

cv
  cue_stick_detection
    Cue stick tip seems off? --> MIN_TIP_AREA, MAX_TIP_AREA
    Cue stick midpoint seems off? --> MIN_CUESTICK_AREA, MAX_CUESTICK_AREA
    Stick mask seems off? --> CUE_LOWER, CUE_UPPER
  hough_circles
    Green dots are flashing everywhere? --> Fix ignore regions in cv/constants.py
