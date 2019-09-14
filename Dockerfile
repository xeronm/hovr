# MAKE: sudo docker build -t dtec.pro/hovr:0.2 .
FROM dtec.pro/hovr:0.1-sdk

LABEL company="dtec.pro" \
      maintainer="Denis Muratov xeronm@gmail.com" \
      example="docker run --name hovr -it --rm --user hovr hovr:0.1" \
      description="Home Video Recorder (based on VLC)" \
      com.name="hovr" \
      com.version="0.1" \
      com.release-date="2018-12-31"

COPY . .
 
