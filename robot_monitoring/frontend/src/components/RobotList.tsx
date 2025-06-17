import React, { useState, useEffect } from "react";
import {
  Grid,
  Card,
  CardContent,
  Typography,
  Box,
  Chip,
  Alert,
  Snackbar,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  TextField,
  DialogContentText,
} from "@mui/material";
import BatteryFullIcon from "@mui/icons-material/BatteryFull";
import ThermostatIcon from "@mui/icons-material/Thermostat";
import SpeedIcon from "@mui/icons-material/Speed";
import LocationOnIcon from "@mui/icons-material/LocationOn";
import EditIcon from "@mui/icons-material/Edit";
import DeleteIcon from "@mui/icons-material/Delete";
import { styled } from "@mui/material/styles";
import { getCookie } from "../utils/cookies";
import RobotManager from "./RobotManager";

interface RobotData {
  robot_id: string;
  position: { x: number; y: number; z: number };
  speed: number;
  temperature: number;
  battery_level: number;
  motor_status: string;
  operation_state: string;
  status: string;
  error_code?: string;
  timestamp: string;
}

interface AlarmData {
  open: boolean;
  message: string;
  severity: "warning" | "error" | "success";
  robotId?: string;
  timestamp?: string;
}

interface RobotEditDialogProps {
  open: boolean;
  robot: RobotData | null;
  onClose: () => void;
  onUpdate: (robotId: string, operationState: string) => void;
  onDelete: (robotId: string) => void;
}

const StyledCard = styled(Card)(({ theme }) => ({
  height: "100%",
  display: "flex",
  flexDirection: "column",
  background: "rgba(30, 30, 30, 0.7)",
  backdropFilter: "blur(10px)",
  borderRadius: "12px",
  transition: "transform 0.2s ease-in-out",
  "&:hover": {
    transform: "translateY(-5px)",
  },
}));

const StatusChip = styled(Chip)(({ theme }) => ({
  borderRadius: "6px",
  fontWeight: "bold",
  textTransform: "uppercase",
  fontSize: "0.75rem",
}));

const InfoBox = styled(Box)(({ theme }) => ({
  display: "flex",
  alignItems: "center",
  padding: "8px",
  borderRadius: "8px",
  background: "rgba(255, 255, 255, 0.05)",
  marginBottom: "8px",
  "& .MuiSvgIcon-root": {
    marginRight: theme.spacing(1),
  },
  "& .MuiTypography-root": {
    fontWeight: 500,
  },
}));

const RobotEditDialog: React.FC<RobotEditDialogProps> = ({
  open,
  robot,
  onClose,
  onUpdate,
  onDelete,
}) => {
  const [operationState, setOperationState] = useState(
    robot?.operation_state || "running"
  );
  const [confirmOpen, setConfirmOpen] = useState(false);

  useEffect(() => {
    if (robot) {
      setOperationState(robot.operation_state);
    }
  }, [robot]);

  const handleDelete = () => {
    if (robot) {
      onDelete(robot.robot_id);
      onClose();
    }
  };

  return (
    <>
      <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
        <DialogTitle>Robot Yönetimi: {robot?.robot_id}</DialogTitle>
        <DialogContent>
          <FormControl fullWidth sx={{ mt: 2 }}>
            <InputLabel>Operasyon Durumu</InputLabel>
            <Select
              value={operationState}
              label="Operasyon Durumu"
              onChange={(e) => setOperationState(e.target.value)}
            >
              <MenuItem value="running">Çalışıyor</MenuItem>
              <MenuItem value="idle">Beklemede</MenuItem>
              <MenuItem value="maintenance">Bakımda</MenuItem>
              <MenuItem value="error">Hata</MenuItem>
            </Select>
          </FormControl>
        </DialogContent>
        <DialogActions sx={{ justifyContent: "space-between", p: 2 }}>
          <Button
            onClick={() => setConfirmOpen(true)}
            variant="outlined"
            color="error"
            startIcon={<DeleteIcon />}
          >
            Robotu Sil
          </Button>
          <Box>
            <Button onClick={onClose}>İptal</Button>
            <Button
              onClick={() => {
                if (robot) {
                  onUpdate(robot.robot_id, operationState);
                  onClose();
                }
              }}
              variant="contained"
            >
              Kaydet
            </Button>
          </Box>
        </DialogActions>
      </Dialog>

      <Dialog open={confirmOpen} onClose={() => setConfirmOpen(false)}>
        <DialogTitle>Robotu Silmeyi Onayla</DialogTitle>
        <DialogContent>
          <DialogContentText>
            Bu işlem geri alınamaz. "{robot?.robot_id}" isimli robotu kalıcı
            olarak silmek istediğinizden emin misiniz?
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setConfirmOpen(false)}>İptal</Button>
          <Button onClick={handleDelete} color="error" variant="contained">
            Sil
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
};

const RobotList: React.FC = () => {
  const [robotData, setRobotData] = useState<RobotData[]>([]);
  const [alarm, setAlarm] = useState<AlarmData>({
    open: false,
    message: "",
    severity: "warning",
  });
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [selectedRobot, setSelectedRobot] = useState<RobotData | null>(null);

  useEffect(() => {
    // İlk veri çekme
    fetchRobots();

    // Her 2 saniyede bir veri güncelleme
    const interval = setInterval(() => {
      fetchRobots();
    }, 2000);

    // Component unmount olduğunda interval'i temizle
    return () => clearInterval(interval);
  }, []);

  const fetchRobots = async () => {
    try {
      // Önce tüm robotları al
      const robotsResponse = await fetch("http://localhost:8000/api/robots/");
      if (!robotsResponse.ok) {
        console.error("Robotlar alınamadı:", robotsResponse.status);
        return;
      }
      const robots = await robotsResponse.json();

      // Sonra her robotun son verilerini al
      const robotDataPromises = robots.map(async (robot: any) => {
        try {
          const dataResponse = await fetch(
            `http://localhost:8000/api/robot-data/${robot.robot_id}/latest/`
          );
          if (dataResponse.ok) {
            const data = await dataResponse.json();
            return {
              ...robot,
              temperature: data?.temperature || 0,
              speed: data?.speed || 0,
              battery_level: data?.battery_level || 0,
              position: data?.position || { x: 0, y: 0, z: 0 },
              motor_status: data?.motor_status || "idle",
            };
          }
        } catch (error) {
          console.error(`Robot ${robot.robot_id} verileri alınamadı:`, error);
          return robot;
        }
      });

      const updatedRobots = await Promise.all(robotDataPromises);
      setRobotData(updatedRobots.filter(Boolean));
    } catch (error) {
      console.error("Robotlar alınamadı:", error);
    }
  };

  const handleRemoveRobot = async (robotId: string) => {
    try {
      const csrfToken = getCookie("csrftoken");
      const response = await fetch(
        `http://localhost:8000/api/robots/${robotId}/`,
        {
          method: "DELETE",
          headers: {
            "X-CSRFToken": csrfToken || "",
          },
          credentials: "include",
        }
      );

      if (response.ok) {
        fetchRobots();
      }
    } catch (error) {
      console.error("Robot silinirken hata:", error);
    }
  };

  const handleUpdateOperationState = async (
    robotId: string,
    operationState: string
  ) => {
    try {
      const csrfToken = getCookie("csrftoken");
      const response = await fetch(
        `http://localhost:8000/api/robots/${robotId}/operation/`,
        {
          method: "PUT",
          headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrfToken || "",
          },
          body: JSON.stringify({ operation_state: operationState }),
        }
      );

      if (response.ok) {
        fetchRobots();
        setEditDialogOpen(false);
        setSelectedRobot(null);
      } else {
        console.error("Robot durumu güncellenemedi:", await response.text());
      }
    } catch (error) {
      console.error("Bağlantı hatası:", error);
    }
  };

  const getStatusColor = (operation_state: string) => {
    switch (operation_state) {
      case "running":
        return "success";
      case "idle":
        return "warning";
      case "error":
        return "error";
      case "maintenance":
        return "info";
      default:
        return "default";
    }
  };

  return (
    <>
      <Box sx={{ p: 3, position: "relative" }}>
        <RobotManager onRobotChange={fetchRobots} />
        <Grid container spacing={3}>
          {robotData.map((robot) => (
            <Grid item xs={12} sm={6} md={4} lg={3} key={robot.robot_id}>
              <StyledCard>
                <CardContent>
                  <Box
                    sx={{
                      display: "flex",
                      justifyContent: "space-between",
                      alignItems: "center",
                    }}
                  >
                    <Typography
                      variant="h6"
                      component="div"
                      sx={{ fontWeight: "bold" }}
                    >
                      {robot.robot_id}
                    </Typography>
                    <IconButton
                      size="small"
                      onClick={() => {
                        setSelectedRobot(robot);
                        setEditDialogOpen(true);
                      }}
                    >
                      <EditIcon />
                    </IconButton>
                  </Box>
                  <StatusChip
                    label={robot.operation_state}
                    color={
                      robot.operation_state === "running"
                        ? "success"
                        : robot.operation_state === "error"
                        ? "error"
                        : robot.operation_state === "maintenance"
                        ? "warning"
                        : "default"
                    }
                  />
                  <Box sx={{ mt: 2, flexGrow: 1 }}>
                    <InfoBox>
                      <ThermostatIcon fontSize="small" />
                      <Typography variant="body2">
                        {robot.temperature?.toFixed(2)}°C
                      </Typography>
                    </InfoBox>
                    <InfoBox>
                      <BatteryFullIcon fontSize="small" />
                      <Typography variant="body2">
                        {robot.battery_level?.toFixed(2)}%
                      </Typography>
                    </InfoBox>
                    <InfoBox>
                      <SpeedIcon fontSize="small" />
                      <Typography variant="body2">
                        {robot.speed?.toFixed(2)} m/s
                      </Typography>
                    </InfoBox>
                    <InfoBox>
                      <LocationOnIcon fontSize="small" />
                      <Typography variant="body2">
                        X: {robot.position?.x?.toFixed(2)}, Y:{" "}
                        {robot.position?.y?.toFixed(2)}, Z:{" "}
                        {robot.position?.z?.toFixed(2)}
                      </Typography>
                    </InfoBox>
                  </Box>
                </CardContent>
              </StyledCard>
            </Grid>
          ))}
        </Grid>
      </Box>

      <RobotEditDialog
        open={editDialogOpen}
        robot={selectedRobot}
        onClose={() => setEditDialogOpen(false)}
        onUpdate={handleUpdateOperationState}
        onDelete={handleRemoveRobot}
      />

      <Snackbar
        open={alarm.open}
        autoHideDuration={6000}
        anchorOrigin={{ vertical: "top", horizontal: "right" }}
        onClose={() => setAlarm((prev) => ({ ...prev, open: false }))}
      >
        <Alert
          severity={alarm.severity}
          variant="filled"
          sx={{
            width: "100%",
            "& .MuiAlert-message": {
              width: "100%",
            },
          }}
        >
          <Box sx={{ display: "flex", flexDirection: "column", gap: 0.5 }}>
            <Typography variant="subtitle2" sx={{ fontWeight: "bold" }}>
              {alarm.robotId}
            </Typography>
            <Typography>{alarm.message}</Typography>
            <Typography variant="caption" sx={{ alignSelf: "flex-end" }}>
              {alarm.timestamp}
            </Typography>
          </Box>
        </Alert>
      </Snackbar>
    </>
  );
};

export default RobotList;
