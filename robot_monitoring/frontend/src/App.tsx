import React from "react";
import { Container, ThemeProvider, createTheme } from "@mui/material";
import RobotList from "./components/RobotList";
import AlarmList from "./components/AlarmList";

const theme = createTheme({
  palette: {
    mode: "dark",
    background: {
      default: "#1e1e1e",
      paper: "#2d2d2d",
    },
    primary: {
      main: "#90caf9",
    },
    secondary: {
      main: "#ce93d8",
    },
  },
});

function App() {
  return (
    <ThemeProvider theme={theme}>
      <div
        style={{
          backgroundColor: "#1e1e1e",
          minHeight: "100vh",
          margin: 0,
          padding: 0,
        }}
      >
        <Container sx={{ pt: 2, pb: 2 }}>
          <h1
            style={{
              color: "#fff",
              margin: 0,
              marginBottom: "20px",
            }}
          >
            Robot İzleme Sistemi
          </h1>
          <RobotList />
        </Container>
        <AlarmList />
      </div>
    </ThemeProvider>
  );
}

export default App;
