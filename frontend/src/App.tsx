import { defineStepper } from "@stepperize/react";
import Footer from "./components/footer";
import Header from "./components/header";
import ModelViewer from "./components/model-viewer";
import StepNav from "./components/stepper/step-nav";
import Steps from "./components/stepper/steps";
import { ThemeProvider } from "./components/theme-provider";
import { Card } from "./components/ui/card";
import useFitObjStore from "./store/useFitObjStore";
import useObjStore from "./store/useObjStore";

function App() {
	const { useStepper } = defineStepper(
		{ id: "generate", title: "Generate 3D-Model" },
		{ id: "tryon", title: "Try on clothes with your 3D-Model" }
	);
	const stepper = useStepper();

	const { obj } = useObjStore();
	const { fitObj } = useFitObjStore();

	return (
		<ThemeProvider defaultTheme="system" storageKey="vite-ui-theme">
			<div className="flex flex-col bg-background w-screen h-screen">
				<Header />
				<main className="flex flex-col flex-1 px-12 p-4 h-full">
					<div className="gap-4 grid grid-cols-5 h-full">
						<Steps stepper={stepper} />
						<Card className="col-span-2 select-none">
							{fitObj ? (
								<ModelViewer obj={fitObj} />
							) : obj ? (
								<ModelViewer obj={obj} />
							) : (
								<span className="flex justify-center items-center w-full h-full text-center">
									No model generated yet. <br />
									Please generate a 3D model first.
								</span>
							)}
						</Card>
					</div>
					<StepNav stepper={stepper} />
				</main>
				<Footer />
			</div>
		</ThemeProvider>
	);
}

export default App;
