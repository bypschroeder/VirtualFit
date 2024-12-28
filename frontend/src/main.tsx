import "@/styles/globals.css";
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import App from "./App.tsx";
import { CameraProvider } from "./components/ui/camera/camera-provider.tsx";

createRoot(document.getElementById("root")!).render(
	<StrictMode>
		<CameraProvider>
			<App />
		</CameraProvider>
	</StrictMode>
);
