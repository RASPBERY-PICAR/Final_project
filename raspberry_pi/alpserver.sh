docker run --rm -t -p 8080:8080 -v license:/license \
  -e TOKEN=5a9ec352bb301702f6ca489a04190b81b7a6805b -e LICENSE_KEY=CYwYq32kXK \
  platerecognizer/alpr-raspberry-pi
