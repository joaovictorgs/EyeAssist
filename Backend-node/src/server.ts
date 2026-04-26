import express from "express";

const app = express();
const port = 3000;

app.get("/", (req, res) => {
  res.send("Get route");
});

app.post("/", (req, res) => {
  res.send("post route");
});

app.get("/health", (req, res) => {
  res.json({ ok: true });
});

app.listen(port, () => {
  console.log("server in http://localhost:" + port);
});
