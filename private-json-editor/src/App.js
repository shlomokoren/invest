import React, { useEffect, useRef, useState } from "react";
import JSONEditor from "jsoneditor";
import "jsoneditor/dist/jsoneditor.css";
import { gapi } from "gapi-script";

const CLIENT_ID =
  "593104739330-m7fph6gsabfl6vcc5q799sf14cshajgu.apps.googleusercontent.com";
//const API_KEY = "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";
const API_KEY = "AIzaSyDP-zgfYrkrs5nLezUN_aqUUaP7Z90wg2Y";
const FILE_ID = "1zeXS_Howx8uD0KvQbk3TtD6NVKZvEqPE";
const SCOPES = "https://www.googleapis.com/auth/drive.file";

function App() {
  const editorRef = useRef(null);
  const containerRef = useRef(null);
  const [signedIn, setSignedIn] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Ensure Google API script is loaded
    const checkGapiLoaded = setInterval(() => {
      if (window.gapi) {
        clearInterval(checkGapiLoaded);
        initClient();
      }
    }, 100);
  }, []);

  const initClient = () => {
    window.gapi.load("client:auth2", () => {
      window.gapi.client
        .init({
          apiKey: API_KEY,
          clientId: CLIENT_ID,
          discoveryDocs: [
            "https://www.googleapis.com/discovery/v1/apis/drive/v3/rest",
          ],
          scope: SCOPES,
        })
        .then(() => {
          const authInstance = window.gapi.auth2.getAuthInstance();
          setSignedIn(authInstance.isSignedIn.get());
          authInstance.isSignedIn.listen((isSignedIn) => {
            setSignedIn(isSignedIn);
            if (isSignedIn) {
              loadJSON();
            }
          });
          setLoading(false);
        })
        .catch((err) => {
          console.error("Error initializing Google API", err);
          setLoading(false);
        });
    });
  };

  const handleSignIn = () => {
    window.gapi.auth2
      .getAuthInstance()
      .signIn()
      .catch((err) => {
        console.error("Sign-in error", err);
      });
  };

  const handleSignOut = () => {
    window.gapi.auth2.getAuthInstance().signOut();
  };

  const loadJSON = () => {
    window.gapi.client.drive.files
      .get({
        fileId: FILE_ID,
        alt: "media",
      })
      .then((res) => {
        if (containerRef.current) {
          if (!editorRef.current) {
            editorRef.current = new JSONEditor(containerRef.current, {
              mode: "tree",
            });
          }
          editorRef.current.set(res.result);
        }
      })
      .catch((err) => {
        console.error("Error loading JSON", err);
      });
  };

  const saveJSON = () => {
    if (!editorRef.current) return;
    const updated = editorRef.current.get();
    const fileContent = new Blob([JSON.stringify(updated, null, 2)], {
      type: "application/json",
    });
    const metadata = {
      name: "data_invest_dev.json",
      mimeType: "application/json",
    };

    const form = new FormData();
    form.append(
      "metadata",
      new Blob([JSON.stringify(metadata)], { type: "application/json" })
    );
    form.append("file", fileContent);

    fetch(
      `https://www.googleapis.com/upload/drive/v3/files/${FILE_ID}?uploadType=multipart`,
      {
        method: "PATCH",
        headers: new Headers({
          Authorization: "Bearer " + window.gapi.auth.getToken().access_token,
        }),
        body: form,
      }
    )
      .then(() => alert("File updated successfully!"))
      .catch((err) => console.error("Error saving JSON", err));
  };

  if (loading) return <p>Loading Google API...</p>;

  return (
    <div>
      {!signedIn ? (
        <button onClick={handleSignIn}>Sign In with Google</button>
      ) : (
        <>
          <button onClick={handleSignOut}>Sign Out</button>
          <div
            ref={containerRef}
            style={{ height: "600px", marginTop: "10px" }}
          ></div>
          <button onClick={saveJSON}>Save to Google Drive</button>
        </>
      )}
    </div>
  );
}

export default App;
