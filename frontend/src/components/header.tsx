import { ModeToggle } from "./mode-toggle";

const Header = () => {
	return (
		<header className="flex justify-between items-center border-secondary px-12 p-4 border-b w-full">
			<h1 className="font-semibold text-2xl">VirtualFit</h1>
			<ModeToggle />
		</header>
	);
};

export default Header;
