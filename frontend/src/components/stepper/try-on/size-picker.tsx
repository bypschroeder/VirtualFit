import { useEffect, useState } from "react";
import { Button } from "../../ui/button";

const SizePicker = () => {
	const sizes = ["XS", "S", "M", "L", "XL", "XXL"];
	const [selectedSize, setSelectedSize] = useState<string | null>(
		sizes[0] || null
	);

	const handleSelect = (size: string) => {
		setSelectedSize(size);
	};

	useEffect(() => {
		console.log(`Selected size: ${selectedSize}`);
	}, [selectedSize]);
	return (
		<div className="flex items-center">
			{sizes.map((size) => (
				<Button
					variant={size === selectedSize ? "default" : "outline"}
					className="rounded-none w-10"
					key={size}
					onClick={() => handleSelect(size)}
				>
					{size}
				</Button>
			))}
		</div>
	);
};

export default SizePicker;
