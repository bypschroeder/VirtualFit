import { defineStepper } from "@stepperize/react";
import { useEffect } from "react";
import Footer from "./components/footer";
import Header from "./components/header";
import ModelDisplay from "./components/model-display";
import StepNav from "./components/stepper/step-nav";
import Steps from "./components/stepper/steps";
import { ThemeProvider } from "./components/theme-provider";
import useFitObjStore from "./store/useFitObjStore";
import useObjStore from "./store/useObjStore";

function App() {
	// Stepper
	const { useStepper } = defineStepper(
		{ id: "generate", title: "Generate 3D-Model" },
		{ id: "tryon", title: "Try on clothes with your 3D-Model" }
	);
	const stepper = useStepper();

	// State Management
	const { obj } = useObjStore();
	const { fitObj } = useFitObjStore();

	// Reset Stepper if no models exist
	useEffect(() => {
		if (!obj && !fitObj) {
			stepper.reset();
		}
	}, [obj, fitObj, stepper]);

	return (
		<ThemeProvider defaultTheme="system" storageKey="vite-ui-theme">
			<div className="flex flex-col bg-background w-screen h-screen">
				<Header />
				<main className="flex flex-col flex-1 px-12 p-4 h-full">
					<div className="gap-4 grid grid-cols-5 h-full">
						<Steps stepper={stepper} />
						<ModelDisplay />
					</div>
					<StepNav stepper={stepper} />
				</main>
				<Footer />
			</div>
		</ThemeProvider>
	);
}

export default App;
