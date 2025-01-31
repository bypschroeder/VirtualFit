import GenerateStep from "./generate/generate-step";
import TryOnStep from "./try-on/try-on-step";

interface Step {
	id: "generate" | "tryon";
	title: string;
}

interface Stepper<T extends readonly Step[]> {
	when: <Id extends T[number]["id"]>(
		id: Id,
		whenFn: (step: Extract<T[number], { id: Id }>) => JSX.Element,
		elseFn?: (step: Exclude<T[number], { id: Id }>) => JSX.Element
	) => JSX.Element;
}

interface StepsProps {
	stepper: Stepper<
		[
			{ readonly id: "generate"; readonly title: "Generate 3D-Model" },
			{
				readonly id: "tryon";
				readonly title: "Try on clothes with your 3D-Model";
			}
		]
	>;
}

const Steps = ({ stepper }: StepsProps) => {
	return (
		<div className="flex flex-col gap-4 col-span-3">
			{stepper.when("generate", () => (
				<GenerateStep />
			))}
			{stepper.when("tryon", () => (
				<TryOnStep />
			))}
		</div>
	);
};

export default Steps;
