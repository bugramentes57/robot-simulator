import React, { useState, useEffect } from "react";
import {
  List,
  ListItem,
  ListItemText,
  Typography,
  Paper,
  Chip,
  IconButton,
  Drawer,
  Badge,
  Snackbar,
  Alert,
  Button,
  Box,
} from "@mui/material";
import ErrorIcon from "@mui/icons-material/Error";
import WarningIcon from "@mui/icons-material/Warning";
import BatteryAlertIcon from "@mui/icons-material/BatteryAlert";
import WhatshotIcon from "@mui/icons-material/Whatshot";
import CheckCircleIcon from "@mui/icons-material/CheckCircle";
import NotificationsIcon from "@mui/icons-material/Notifications";

interface Alarm {
  _id: string;
  robot_id: string;
  timestamp: string;
  alarm_type: string;
  message: string;
  temperature?: number;
  battery_level?: number;
}

const AlarmList: React.FC = () => {
  const [alarms, setAlarms] = useState<Alarm[]>([]);
  const [drawerOpen, setDrawerOpen] = useState(false);

  // Son 5 dakikalık alarmları çeken fonksiyon
  const fetchRecentAlarms = async () => {
    try {
      const fiveMinutesAgo = new Date(Date.now() - 5 * 60 * 1000).toISOString();
      const response = await fetch(
        `http://localhost:8000/api/alarms/?after=${fiveMinutesAgo}`
      );
      if (!response.ok)
        throw new Error(`HTTP error! status: ${response.status}`);
      const data = await response.json();

      // Sadece yeni alarmları ekle ve 3 saniye sonra kaldır
      if (data.length > 0) {
        data.forEach((newAlarm: Alarm) => {
          if (!alarms.find((a) => a._id === newAlarm._id)) {
            setAlarms((prev) => [...prev, newAlarm]);
            // 3 saniye sonra alarmı kaldır
            setTimeout(() => {
              setAlarms((prev) => prev.filter((a) => a._id !== newAlarm._id));
            }, 3000);
          }
        });
      }
    } catch (error) {
      console.error("Alarm verileri alınamadı:", error);
    }
  };

  useEffect(() => {
    fetchRecentAlarms();
    const interval = setInterval(fetchRecentAlarms, 2000);
    return () => clearInterval(interval);
  }, []);

  const getAlarmIcon = (alarmType: string) => {
    switch (alarmType) {
      case "system_error":
        return <ErrorIcon color="error" />;
      case "high_temperature":
        return <WhatshotIcon color="error" />;
      case "low_battery":
        return <BatteryAlertIcon color="warning" />;
      default:
        return <WarningIcon color="warning" />;
    }
  };

  return (
    <>
      <IconButton
        color="inherit"
        onClick={() => setDrawerOpen(true)}
        sx={{ position: "fixed", top: 10, right: 10, zIndex: 1000 }}
      >
        <Badge badgeContent={alarms.length} color="error">
          <NotificationsIcon />
        </Badge>
      </IconButton>

      {/* Aktif alarmlar listesi - sol üstte gösterilecek */}
      <Box
        sx={{
          position: "fixed",
          top: 10,
          left: 10,
          zIndex: 1000,
          width: "400px",
        }}
      >
        {alarms.map((alarm) => (
          <Alert
            key={alarm._id}
            severity={alarm.alarm_type === "system_error" ? "error" : "warning"}
            sx={{
              mb: 1,
              boxShadow: 2,
              "& .MuiAlert-message": {
                width: "100%",
              },
            }}
          >
            <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
              {getAlarmIcon(alarm.alarm_type)}
              <div style={{ flex: 1 }}>
                <Typography variant="subtitle2">{alarm.robot_id}</Typography>
                <Typography variant="body2">{alarm.message}</Typography>
                <Typography variant="caption" color="text.secondary">
                  {new Date(alarm.timestamp).toLocaleTimeString()}
                </Typography>
              </div>
            </div>
          </Alert>
        ))}
      </Box>

      {/* Drawer kısmı aynı kalacak */}
      <Drawer
        anchor="right"
        open={drawerOpen}
        onClose={() => setDrawerOpen(false)}
      >
        <Paper sx={{ width: 350, p: 2, height: "100%", overflow: "auto" }}>
          <Typography variant="h6" gutterBottom>
            Aktif Alarmlar ({alarms.length})
          </Typography>
          <List>
            {alarms.map((alarm) => (
              <ListItem key={alarm._id} divider>
                <ListItemText
                  primary={
                    <div
                      style={{
                        display: "flex",
                        alignItems: "center",
                        gap: "8px",
                      }}
                    >
                      {getAlarmIcon(alarm.alarm_type)}
                      <span>{alarm.robot_id}</span>
                      <Chip
                        label={alarm.message}
                        color={
                          alarm.alarm_type === "system_error"
                            ? "error"
                            : "warning"
                        }
                        size="small"
                      />
                    </div>
                  }
                  secondary={new Date(alarm.timestamp).toLocaleString()}
                />
              </ListItem>
            ))}
          </List>
        </Paper>
      </Drawer>
    </>
  );
};

export default AlarmList;
