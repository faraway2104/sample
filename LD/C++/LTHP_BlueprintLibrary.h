// Fill out your copyright notice in the Description page of Project Settings.

#pragma once

#include "CoreMinimal.h"
#include "Kismet/BlueprintFunctionLibrary.h"
#include "LTHP_BlueprintLibrary.generated.h"

/**
 * 
 */
UCLASS()
class LOCALIZETEXTHELPERPLUGIN_API ULTHP_BlueprintLibrary : public UBlueprintFunctionLibrary
{
public:
	GENERATED_BODY()

public:
	UFUNCTION(BlueprintCallable, Category="LTHP")
	static bool ImportLocalizedText(const FString JsonPath);

public:
	UFUNCTION(BlueprintCallable, Category="LTHP")
	static bool ImportStringTablesFromCSVInDirectory(const FString InAssetDir, const FString InDirectory);

	UFUNCTION(BlueprintCallable, Category="LTHP")
	static bool ImportStringTableFromCSV(const FString InAssetDir, const FString InAssetName, const FString InCSVPath);

	UFUNCTION(BlueprintCallable, Category="LTHP")
	static bool ImportLocalizedTextFromPO(const FString InPOPath);
};
