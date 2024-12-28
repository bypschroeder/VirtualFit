import { Moon, Sun } from "lucide-react";

import { useTheme } from "@/components/theme-provider";
import { Button } from "@/components/ui/button";

export function ModeToggle() {
	const { theme, setTheme } = useTheme();

	const toggleTheme = () => {
		setTheme(theme === "light" ? "dark" : "light");
	};

	return (
		<Button
			variant={"outline"}
			size={"icon"}
			className="rounded-full"
			onClick={toggleTheme}
		>
			{theme === "light" ? (
				<Moon className="w-[1.2rem] h-[1.2rem] transition-all dark:-rotate-90 dark:scale-0 rotate-0 scale-100" />
			) : (
				<Sun className="w-[1.2rem] h-[1.2rem] transition-all dark:-rotate-0 dark:scale-100 rotate-90 scale-0" />
			)}
			<span className="sr-only">Toggle theme</span>
		</Button>
	);
}
