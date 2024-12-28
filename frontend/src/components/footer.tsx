import { Github } from "lucide-react";
import { Button } from "./ui/button";

const Footer = () => {
	return (
		<footer className="flex justify-between items-center border-secondary px-12 p-4 border-t w-full">
			<span className="text-muted-foreground text-sm">
				VirtualFit is a project by the Institute for Information Systems (
				<a
					href="https://www.iisys.de/"
					target="_blank"
					rel="noopener noreferrer"
					className="text-primary"
				>
					iisys
				</a>
				) at{" "}
				<a
					href="https://www.hof-university.de/"
					target="_blank"
					rel="noopener noreferrer"
					className="text-primary"
				>
					Hof University of Applied Sciences
				</a>
			</span>
			<a
				href="https://github.com/bypschroeder/VirtualFit"
				target="_blank"
				rel="noopener noreferrer"
			>
				<Button variant={"outline"} size={"icon"} className="rounded-full">
					<Github size={32} />
				</Button>
			</a>
		</footer>
	);
};

export default Footer;
