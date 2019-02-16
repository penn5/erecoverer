# How eRecovery downloads files

- Well, it's weird.
- First, it requests to find the most recent update. It will try this 4 times, twice for packagetype full and twice for packagetype full_indicator
- After it has the latest package, it requests filelist.xml. This is generated from `components[0]/full/filelist.xml`. Note the `/` before `full`. After retrieving the filelist, it parses it and progresses to the next step. **Note the order here.**
- eRecovery changes page to the downloading page, status 0%. Now it initiates a request to the UpdateReport.action page. This page is not important; it is just telemetry. If it returns 404, eRecovery tries 3 times and ignores the error.
- Next, eRecovery attempts to download update.zip. It sends a request to `components[0]full/update.zip`. Note the lack of a `/` before `full`. Its method for fetching this file **does not fully comply with HTTP. See below!**
- To fetch this file, it reads `/data/update/package_cache/update.zip` and checks how much is already downloaded. If this file exists, it will execute a request with `Range: bytes <filesize>-`, otherwise it uses 0 as filesize. This request is dispatches according to HTTP, and it checks some of the headers. If they're okay, it reads some of the data, and abruptly aborts the connection, leading to 104 Connection Reset by Peer. It then sends another request to the same file, with the next needed range. Something about how it does this causes non-threaded HTTP servers to fail and deadlock, hence why Python 3.7 is needed.
- Finally, it verifies the md5s from filelist.xml and installs the packages.

