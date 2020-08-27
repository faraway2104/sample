// Fill out your copyright notice in the Description page of Project Settings.


#include "LTHP_BlueprintLibrary.h"

#include "AssetToolsModule.h"
#include "AssetRegistryModule.h"
#include "Internationalization/StringTable.h"
#include "Internationalization/StringTableCore.h"
#include "LocalizationModule.h"
#include "Interfaces/IMainFrameModule.h"
#include "LocalizationCommandletTasks.h"
#include "LocalizationTargetTypes.h"
#include "Misc/LocalTimestampDirectoryVisitor.h"
#include "Misc/FileHelper.h"
#include "Serialization/JsonReader.h"
#include "EditorAssetLibrary.h"

bool ULTHP_BlueprintLibrary::ImportLocalizedText(const FString JsonPath)
{
	FString JsonStr;
	FFileHelper::LoadFileToString(JsonStr, *JsonPath);
	TSharedRef<TJsonReader<TCHAR>> JsonReader = TJsonReaderFactory<TCHAR>::Create(JsonStr);
	TSharedPtr<FJsonObject> JsonObject = MakeShareable(new FJsonObject());
	if (FJsonSerializer::Deserialize(JsonReader, JsonObject) && JsonObject.IsValid())
	{
        const FString fileName = FPaths::GetCleanFilename(*JsonPath);
		const FString targetName = FPaths::ChangeExtension(fileName, "");

		ULocalizationTarget* Target = ILocalizationModule::Get().GetLocalizationTargetByName(*targetName, false);
		if(Target == nullptr)
		{
			return false;
		}

		bool bCanRun = true;
		FString NativeCulture;
		bCanRun = bCanRun && JsonObject->TryGetStringField(TEXT("NativeCulture"), NativeCulture);

		FString StringTableAssetDir;
		bCanRun = bCanRun && JsonObject->TryGetStringField(TEXT("StringTableAssetDir"), StringTableAssetDir);

		FString StringTableCSVDir;
		bCanRun = bCanRun && JsonObject->TryGetStringField(TEXT("StringTableCSVDir"), StringTableCSVDir);

		FString PODir;
		bCanRun = bCanRun && JsonObject->TryGetStringField(TEXT("PODir"), PODir);

		TArray<FString> StringTableNames;
		bCanRun = bCanRun && JsonObject->TryGetStringArrayField(TEXT("StringTableName"), StringTableNames);

		if(!bCanRun)
		{
			return false;
		}

		const TOptional<FString> CultureName = NativeCulture;
		const int32 CultureIndex = Target->Settings.SupportedCulturesStatistics.IndexOfByPredicate([CultureName](const FCultureStatistics& Culture) { return Culture.CultureName == CultureName.GetValue(); });
		if(CultureIndex != INDEX_NONE)
		{
			if(Target->Settings.NativeCultureIndex != CultureIndex)
			{
				Target->Settings.NativeCultureIndex = CultureIndex;
			}
		}

		for(FString AssetName : StringTableNames)
		{
			if( !ImportStringTableFromCSV(StringTableAssetDir, AssetName, StringTableCSVDir + AssetName + ".csv") )
			{
				return false;
			}
		}

		if( !ImportLocalizedTextFromPO(PODir) )
		{
			return false;
		}
	}

	return true;

}

bool ULTHP_BlueprintLibrary::ImportStringTablesFromCSVInDirectory(const FString InAssetDir, const FString InDirectory)
{
    // Get all files in directory
    TArray<FString> directoriesToSkip;
    IPlatformFile &PlatformFile = FPlatformFileManager::Get().GetPlatformFile();
    FLocalTimestampDirectoryVisitor Visitor(PlatformFile, directoriesToSkip, directoriesToSkip, false);
    PlatformFile.IterateDirectory(*InDirectory, Visitor);
    TArray<FString> files;

    for (TMap<FString, FDateTime>::TIterator It(Visitor.FileTimes); It; ++It)
    {
        const FString filePath = It.Key();
        const FString fileName = FPaths::GetCleanFilename(filePath);
		const FString assetName = FPaths::ChangeExtension(fileName, "");

		if( !ImportStringTableFromCSV(InAssetDir, assetName, filePath) )
		{
			return false;
		}
	}

	return true;
}

bool ULTHP_BlueprintLibrary::ImportStringTableFromCSV(const FString InAssetDir, const FString InAssetName, const FString InCSVPath)
{
	// 
	FAssetRegistryModule& AssetRegistryModule = FModuleManager::LoadModuleChecked<FAssetRegistryModule>(FName("AssetRegistry"));
    FAssetData Data = AssetRegistryModule.Get().GetAssetByObjectPath(FName(InAssetDir + "/" + InAssetName + "." + InAssetName));
	UStringTable* TargetStringTable = Cast<UStringTable>(Data.GetAsset());

	// 
	if(TargetStringTable == nullptr)
	{
		FAssetToolsModule& AssetToolsModule = FModuleManager::GetModuleChecked<FAssetToolsModule>("AssetTools");
		TargetStringTable = Cast<UStringTable>(AssetToolsModule.Get().CreateAsset(InAssetName, InAssetDir, UStringTable::StaticClass(), nullptr));
	}

	// 
	if(TargetStringTable != nullptr)
	{
		TargetStringTable->Modify();
		TargetStringTable->GetMutableStringTable()->ImportStrings(InCSVPath);
		UEditorAssetLibrary::SaveAsset(InAssetDir + "/" + InAssetName);
		return true;
	}

	return false;
}

bool ULTHP_BlueprintLibrary::ImportLocalizedTextFromPO(const FString InPOPath)
{
	ULocalizationTarget* Target = ILocalizationModule::Get().GetLocalizationTargetByName("Game", false);
	if(Target == nullptr)
	{
		return false;
	}


	IMainFrameModule& MainFrameModule = FModuleManager::LoadModuleChecked<IMainFrameModule>(TEXT("MainFrame"));
	const TSharedPtr<SWindow>& MainFrameParentWindow = MainFrameModule.GetParentWindow();
	if( !LocalizationCommandletTasks::GatherTextForTarget(MainFrameParentWindow.ToSharedRef(), Target) )
	{
		return false;
	}

	if( !LocalizationCommandletTasks::ImportTextForTarget(MainFrameParentWindow.ToSharedRef(), Target, InPOPath) )
	{
		return false;
	}

	if( !LocalizationCommandletTasks::CompileTextForTarget(MainFrameParentWindow.ToSharedRef(), Target) )
	{
		return false;
	}

	return true;
}

